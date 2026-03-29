import logging
from typing import Any, Dict

from app.core.context import AgentContext
from app.schemas.finance_models import MatchStatus


logger = logging.getLogger(__name__)


class PolicyMatrix:
    """Deterministic enterprise policy matrix for autonomous action gating."""

    @staticmethod
    def evaluate_action_risk(context: AgentContext) -> str:
        """Return a policy decision string based on transaction amount and confidence."""
        threshold = 50000.0
        belief_state: Dict[str, Any] = context.belief_state
        match_confidence = float(belief_state.get("match_confidence", 0.0))
        amount = float(context.transaction.amount)

        logger.info(
            f"[POLICY] Confidence={match_confidence:.4f} | Amount={amount:.2f} | Threshold={threshold:.2f}"
        )

        if amount >= threshold:
            decision = "ESCALATE_TO_HUMAN"
            logger.info(f"[POLICY] Decision={decision}")
            return decision

        if match_confidence >= 0.98:
            decision = "DETERMINISTIC_ALLOW"
            logger.info(f"[POLICY] Decision={decision}")
            return decision

        if match_confidence >= 0.85:
            if "EDGE_FEE_ADJUST" in context.edge_flags:
                decision = "PROBABILISTIC_ALLOW"
                logger.info(f"[POLICY] Decision={decision}")
                return decision
            decision = "ESCALATE_TO_HUMAN"
            logger.info(f"[POLICY] Decision={decision}")
            return decision

        decision = "ESCALATE_TO_HUMAN"
        logger.info(f"[POLICY] Decision={decision}")
        return decision
