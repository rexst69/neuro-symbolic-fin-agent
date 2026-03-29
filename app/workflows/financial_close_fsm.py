from typing import Any

from app.core.context import AgentContext
from app.core.resilient_fsm import ResilientFSM, Transition


def forward_action(context: AgentContext) -> Any:
    """Dummy forward action for financial close progression."""
    context.add_trace("FinancialCloseFSM", "Forward action: period close transition executed.")
    return True


def rollback_action(context: AgentContext) -> Any:
    """Dummy rollback action for financial close progression."""
    context.add_trace("FinancialCloseFSM", "Rollback action: period close transition reversed.")
    return True


class FinancialCloseFSM(ResilientFSM):
    """FSM for financial close workflow transitions."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="PERIOD_OPEN")
        self.freeze_transition = Transition(
            from_state="PERIOD_OPEN",
            to_state="SUBLEDGER_FREEZE",
            forward_action=forward_action,
            rollback_action=rollback_action,
            max_retries=3,
        )

    def process(self) -> Any:
        """Execute the financial close transition."""
        return self.execute_transition(self.freeze_transition)
