from typing import Any, Dict

from app.core.context import AgentContext
from app.schemas.finance_models import MatchStatus


class PolicyMatrix:
    """Deterministic enterprise policy matrix for autonomous action gating."""

    @staticmethod
    def evaluate_action_risk(context: AgentContext) -> str:
        """Return a policy decision string based on transaction amount and confidence."""
        if context.transaction.amount >= 50000.0:
            return "ESCALATE_TO_HUMAN"

        belief_state: Dict[str, Any] = context.belief_state
        match_confidence = float(belief_state.get("match_confidence", 0.0))

        if match_confidence >= 0.98:
            return "DETERMINISTIC_ALLOW"

        if match_confidence >= 0.85:
            if "EDGE_FEE_ADJUST" in context.edge_flags:
                return "PROBABILISTIC_ALLOW"
            return "ESCALATE_TO_HUMAN"

        return "ESCALATE_TO_HUMAN"
