from typing import Any

from app.core.context import AgentContext
from app.core.resilient_fsm import ResilientFSM, Transition


def forward_action(context: AgentContext) -> Any:
    """Dummy forward action for reporting progression."""
    context.add_trace("ReportingFSM", "Forward action: report generation executed.")
    return True


def rollback_action(context: AgentContext) -> Any:
    """Dummy rollback action for reporting progression."""
    context.add_trace("ReportingFSM", "Rollback action: report generation reversed.")
    return True


class ReportingFSM(ResilientFSM):
    """FSM for reporting workflow transitions."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="DATA_AGGREGATED")
        self.reporting_transition = Transition(
            from_state="DATA_AGGREGATED",
            to_state="REPORT_GENERATED",
            forward_action=forward_action,
            rollback_action=rollback_action,
            max_retries=3,
        )

    def process(self) -> Any:
        """Execute the reporting transition."""
        return self.execute_transition(self.reporting_transition)
