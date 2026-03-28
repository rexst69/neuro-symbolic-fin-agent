from typing import List, Optional

from app.matching import composite_matcher, exact_matcher, probabilistic_matcher
from app.schemas.audit_models import MatchProposal
from app.schemas.finance_models import Invoice, Transaction


class MatchingEngine:
    """Waterfall orchestrator for transaction-to-invoice matching algorithms."""

    @staticmethod
    def execute_cascade(
        transaction: Transaction,
        open_invoices: List[Invoice],
    ) -> Optional[MatchProposal]:
        """Run exact, probabilistic, and composite matchers in cascade order."""
        proposal = exact_matcher.match(transaction, open_invoices)
        if proposal is not None:
            return proposal

        proposal = probabilistic_matcher.match(transaction, open_invoices)
        if proposal is not None:
            return proposal

        proposal = composite_matcher.match(transaction, open_invoices)
        if proposal is not None:
            return proposal

        return None
