from typing import Any

from app.core.context import AgentContext
from app.core.resilient_fsm import ResilientFSM, Transition


def forward_action(context: AgentContext) -> Any:
    """Dummy forward action for discrepancy progression."""
    context.add_trace("DiscrepancyFSM", "Forward action: discrepancy moved to auto-adjust pending.")
    return True


def rollback_action(context: AgentContext) -> Any:
    """Dummy rollback action for discrepancy progression."""
    context.add_trace("DiscrepancyFSM", "Rollback action: discrepancy transition reversed.")
    return True


class DiscrepancyFSM(ResilientFSM):
    """FSM for discrepancy workflow transitions."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="DETECTED")
        self.discrepancy_transition = Transition(
            from_state="DETECTED",
            to_state="AUTO_ADJUST_PENDING",
            forward_action=forward_action,
            rollback_action=rollback_action,
            max_retries=3,
        )

    def process(self) -> Any:
        """Execute the discrepancy transition."""
        return self.execute_transition(self.discrepancy_transition)
