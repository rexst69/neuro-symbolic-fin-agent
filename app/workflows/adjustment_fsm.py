from typing import Any

from app.core.context import AgentContext
from app.core.resilient_fsm import ResilientFSM, Transition


def forward_action(context: AgentContext) -> Any:
    """Dummy forward action for adjustment progression."""
    context.add_trace("AdjustmentFSM", "Forward action: adjustment journal posted.")
    return True


def rollback_action(context: AgentContext) -> Any:
    """Dummy rollback action for adjustment progression."""
    context.add_trace("AdjustmentFSM", "Rollback action: adjustment journal reversed.")
    return True


class AdjustmentFSM(ResilientFSM):
    """FSM for adjustment workflow transitions."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="ADJUSTMENT_IDENTIFIED")
        self.adjustment_transition = Transition(
            from_state="ADJUSTMENT_IDENTIFIED",
            to_state="JOURNAL_POSTED",
            forward_action=forward_action,
            rollback_action=rollback_action,
            max_retries=3,
        )

    def process(self) -> Any:
        """Execute the adjustment transition."""
        return self.execute_transition(self.adjustment_transition)
