from typing import List, Optional

from app.schemas.finance_models import Invoice, Transaction

try:
    from app.schemas.audit_models import MatchProposal
except ImportError:
    from app.schemas.finance_models import MatchProposal


def match(transaction: Transaction, open_invoices: List[Invoice]) -> Optional[MatchProposal]:
    """Return a mock probabilistic match proposal based on payer-client name equality."""
    if transaction.payer_name is None:
        return None

    payer_name_lower = transaction.payer_name.lower()

    for invoice in open_invoices:
        if invoice.client_name.lower() == payer_name_lower:
            discrepancy = transaction.amount - invoice.balance_due
            return MatchProposal(
                transaction_id=transaction.id,
                invoice_ids=[invoice.id],
                match_confidence=0.85,
                discrepancy_amount=discrepancy,
                match_type="PROBABILISTIC",
            )

    return None
