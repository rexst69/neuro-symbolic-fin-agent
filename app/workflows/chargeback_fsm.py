from typing import Any

from app.core.context import AgentContext
from app.core.resilient_fsm import ResilientFSM, Transition


def forward_action(context: AgentContext) -> Any:
    """Dummy forward action for chargeback progression."""
    context.add_trace("ChargebackFSM", "Forward action: chargeback posted to AR deduction state.")
    return True


def rollback_action(context: AgentContext) -> Any:
    """Dummy rollback action for chargeback progression."""
    context.add_trace("ChargebackFSM", "Rollback action: AR deduction reversed for chargeback.")
    return True


class ChargebackFSM(ResilientFSM):
    """FSM for chargeback workflow transitions."""

    def __init__(self, context: AgentContext):
        super().__init__(context, initial_state="DISPUTE_OPENED")
        self.chargeback_transition = Transition(
            from_state="DISPUTE_OPENED",
            to_state="AR_DEDUCTED",
            forward_action=forward_action,
            rollback_action=rollback_action,
            max_retries=3,
        )

    def process(self) -> Any:
        """Execute the chargeback transition."""
        return self.execute_transition(self.chargeback_transition)
