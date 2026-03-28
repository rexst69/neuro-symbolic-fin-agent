from typing import List, Optional

from app.schemas.finance_models import Invoice, Transaction

try:
    from app.schemas.audit_models import MatchProposal
except ImportError:
    from app.schemas.finance_models import MatchProposal


def match(transaction: Transaction, open_invoices: List[Invoice]) -> Optional[MatchProposal]:
    """Stubbed: N:M Subset-sum optimization for netting multiple invoices to a single payment."""
    return None
