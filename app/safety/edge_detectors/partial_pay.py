import logging

from app.core.context import AgentContext
from app.schemas.finance_models import MatchStatus


logger = logging.getLogger(__name__)


class PartialPayDetector:
    """Detects partial-payment mismatches that exceed fee-like variance thresholds."""

    @staticmethod
    def detect(context: AgentContext) -> None:
        """Append EDGE_PARTIAL_PAY when the underpayment gap exceeds 3% of invoice balance."""
        if context.match_status != MatchStatus.SUGGESTED:
            return
        if not context.matched_invoices:
            return

        invoice = context.matched_invoices[0]
        if context.transaction.amount >= invoice.balance_due:
            return

        gap = invoice.balance_due - context.transaction.amount
        if gap > (invoice.balance_due * 0.03):
            if "EDGE_PARTIAL_PAY" not in context.edge_flags:
                context.edge_flags.append("EDGE_PARTIAL_PAY")
            logger.info(
                f"[EDGE] Type=EDGE_PARTIAL_PAY | Amount={gap:.2f} | "
                f"Description=Partial payment detected for invoice {invoice.id}"
            )
            logger.info(
                "[EDGE_RESOLUTION] Strategy=PARTIAL_PAYMENT_WORKFLOW | "
                "Action=ESCALATE_OR_SPLIT_ALLOCATE"
            )
            context.add_trace("PartialPayDetector", "Partial payment detected, flag added.")
