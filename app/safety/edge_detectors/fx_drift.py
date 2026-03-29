import logging

from app.core.context import AgentContext
from app.schemas.finance_models import MatchStatus


logger = logging.getLogger(__name__)


class FXDriftDetector:
    """Detects potential FX drift when transaction and invoice currencies diverge."""

    @staticmethod
    def detect(context: AgentContext) -> None:
        """Append EDGE_FX_DRIFT when matched invoice currency differs from transaction currency."""
        if context.match_status != MatchStatus.SUGGESTED:
            return
        if not context.matched_invoices:
            return

        invoice = context.matched_invoices[0]
        if context.transaction.currency != invoice.currency:
            if "EDGE_FX_DRIFT" not in context.edge_flags:
                context.edge_flags.append("EDGE_FX_DRIFT")
            logger.info(
                f"[EDGE] Type=EDGE_FX_DRIFT | Amount={context.transaction.amount:.2f} | "
                f"Description=Currency mismatch {context.transaction.currency}->{invoice.currency}"
            )
            logger.info(
                "[EDGE_RESOLUTION] Strategy=FX_REMEASUREMENT_CHECK | "
                "Action=REQUIRE_FX_VALIDATION"
            )
            context.add_trace("FXDriftDetector", "Currency mismatch detected, FX drift flag added.")
