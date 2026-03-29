import logging

from app.core.context import AgentContext
from app.schemas.finance_models import MatchStatus


logger = logging.getLogger(__name__)


class FeeDetector:
    """Detects fee-like payment discrepancies and tags context edge flags."""

    @staticmethod
    def detect(context: AgentContext) -> None:
        """Detect Stripe-like fee variance when a suggested match underpays by up to 3%."""
        if context.match_status != MatchStatus.SUGGESTED:
            return

        for invoice in context.matched_invoices:
            if invoice.balance_due <= 0:
                continue

            discrepancy = invoice.balance_due - context.transaction.amount
            within_fee_band = 0 < discrepancy <= (invoice.balance_due * 0.03)

            if within_fee_band:
                if "EDGE_FEE_ADJUST" not in context.edge_flags:
                    context.edge_flags.append("EDGE_FEE_ADJUST")
                logger.info(
                    f"[EDGE] Type=EDGE_FEE_ADJUST | Amount={discrepancy:.2f} | "
                    f"Description=Fee-like variance detected for invoice {invoice.id}"
                )
                logger.info(
                    "[EDGE_RESOLUTION] Strategy=FEE_VARIANCE_TOLERANCE | "
                    "Action=ALLOW_PROBABILISTIC_REVIEW"
                )
                context.add_trace("FeeDetector", "Fee detected, flag added.")
                return
