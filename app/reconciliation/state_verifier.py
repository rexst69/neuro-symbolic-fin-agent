from app.core.context import AgentContext
from app.core.exceptions import ExternalStateMismatchError


class StateVerifier:
    """Context-driven verification engine for post-execution ERP consistency."""

    @staticmethod
    def verify_erp_state(context: AgentContext) -> bool:
        """Verify that execution artifacts in AgentContext are consistent with expected post state."""
        if context.workflow_state != "POSTED":
            raise ExternalStateMismatchError(
                "Verification requested before workflow reached POSTED state.",
                details={"workflow_state": context.workflow_state},
            )

        execution = context.belief_state.get("last_execution")
        if not execution:
            raise ExternalStateMismatchError(
                "Missing execution record in context belief_state.",
                details={"belief_state_keys": sorted(context.belief_state.keys())},
            )

        if execution.get("action") != "POST_JE":
            raise ExternalStateMismatchError(
                "Unexpected execution action while verifying posted state.",
                details={"action": execution.get("action")},
            )

        if execution.get("connector") not in {"NETSUITE", "SAP"}:
            raise ExternalStateMismatchError(
                "Unsupported connector recorded in execution artifact.",
                details={"connector": execution.get("connector")},
            )

        posted_journal_id = context.belief_state.get("posted_journal_id")
        if not posted_journal_id:
            raise ExternalStateMismatchError(
                "Missing posted journal identifier for reconciliation verification.",
                details={"belief_state_keys": sorted(context.belief_state.keys())},
            )

        context.add_trace(
            "StateVerifier",
            "Execution artifacts verified against expected posted state.",
            {
                "connector": execution.get("connector"),
                "posted_journal_id": posted_journal_id,
            },
        )
        return True
