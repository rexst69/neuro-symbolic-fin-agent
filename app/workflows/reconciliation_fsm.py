from typing import Any, Dict

from app.core.context import AgentContext
from app.core.resilient_fsm import ResilientFSM, Transition


def dummy_post_journal(context: AgentContext) -> Any:
    """Dummy forward action that simulates posting a journal entry to ERP."""
    context.add_trace("ReconciliationFSM", "Forward action: POST to ERP executed.")
    return True


def dummy_reverse_journal(context: AgentContext) -> Any:
    """Dummy rollback action that simulates reversing a journal entry in ERP."""
    context.add_trace("ReconciliationFSM", "Rollback action: REVERSE journal in ERP executed.")
    return True


class ReconciliationFSM(ResilientFSM):
    """Workflow-specific FSM for AR/AP reconciliation journal posting."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="READY_TO_POST")
        self.post_transition = Transition(
            from_state="READY_TO_POST",
            to_state="POSTED",
            forward_action=dummy_post_journal,
            rollback_action=dummy_reverse_journal,
            max_retries=3,
        )

    def process_posting(self) -> Any:
        """Execute the posting transition using resilient retry and rollback semantics."""
        return self.execute_transition(self.post_transition)
