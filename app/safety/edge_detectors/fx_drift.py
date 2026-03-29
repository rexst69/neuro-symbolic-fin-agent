from app.core.context import AgentContext
from app.schemas.finance_models import MatchStatus


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
            context.add_trace("FXDriftDetector", "Currency mismatch detected, FX drift flag added.")
