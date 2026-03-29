from typing import Any, Dict

from app.core.context import AgentContext
from app.core.exceptions import ExternalStateMismatchError, MissingRollbackActionError
from app.core.resilient_fsm import ResilientFSM, Transition
from app.execution.dispatcher import ExecutionDispatcher


def _extract_posted_journal_id(execution_result: Dict[str, Any]) -> str:
    """Extract a canonical posted journal identifier from connector responses."""
    if "internal_id" in execution_result:
        return str(execution_result["internal_id"])

    sap_payload = execution_result.get("d", {})
    if isinstance(sap_payload, dict) and "DocumentNo" in sap_payload:
        return str(sap_payload["DocumentNo"])

    return ""


def post_journal(context: AgentContext) -> Any:
    """Post journal entry through execution dispatcher and persist execution state in context."""
    payload = {
        "transaction_id": context.transaction.id,
        "reference": context.transaction.reference,
        "amount": context.transaction.amount,
        "currency": context.transaction.currency.value,
        "invoice_ids": [invoice.id for invoice in context.matched_invoices],
    }
    execution = ExecutionDispatcher.dispatch("POST_JE", payload, context)
    journal_id = _extract_posted_journal_id(execution.get("result", {}))
    if not journal_id:
        raise ExternalStateMismatchError(
            "Execution succeeded but no posted journal identifier was returned.",
            details={"execution": execution},
        )

    context.belief_state["last_execution"] = execution
    context.belief_state["posted_journal_id"] = journal_id
    context.add_trace(
        "ReconciliationFSM",
        "Forward action completed: journal posted.",
        {"posted_journal_id": journal_id},
    )
    return execution


def reverse_journal(context: AgentContext) -> Any:
    """Reverse previously posted journal entry through execution dispatcher."""
    journal_id = context.belief_state.get("posted_journal_id")
    if not journal_id:
        raise MissingRollbackActionError(
            "Rollback requires a posted journal identifier in context.",
            details={"belief_state_keys": sorted(context.belief_state.keys())},
        )

    reversal = ExecutionDispatcher.dispatch("REVERSE_JE", {"journal_id": journal_id}, context)
    context.belief_state["last_reversal"] = reversal
    context.add_trace(
        "ReconciliationFSM",
        "Rollback action completed: journal reversed.",
        {"posted_journal_id": journal_id},
    )
    return reversal


class ReconciliationFSM(ResilientFSM):
    """Workflow-specific FSM for AR/AP reconciliation journal posting."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="READY_TO_POST")
        self.post_transition = Transition(
            from_state="READY_TO_POST",
            to_state="POSTED",
            forward_action=post_journal,
            rollback_action=reverse_journal,
            max_retries=3,
        )

    def process_posting(self) -> Any:
        """Execute the posting transition using resilient retry and rollback semantics."""
        return self.execute_transition(self.post_transition)
