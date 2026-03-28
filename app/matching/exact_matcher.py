from typing import List, Optional

from app.schemas.finance_models import Invoice, Transaction

try:
    from app.schemas.audit_models import MatchProposal
except ImportError:
    from app.schemas.finance_models import MatchProposal


def match(transaction: Transaction, open_invoices: List[Invoice]) -> Optional[MatchProposal]:
    """Return an exact match proposal when amount and reference criteria are satisfied."""
    reference_lower = transaction.reference.lower()

    for invoice in open_invoices:
        if invoice.balance_due == transaction.amount and invoice.id.lower() in reference_lower:
            return MatchProposal(
                transaction_id=transaction.id,
                invoice_ids=[invoice.id],
                match_confidence=1.0,
                discrepancy_amount=0.0,
                match_type="EXACT",
            )

    return None
