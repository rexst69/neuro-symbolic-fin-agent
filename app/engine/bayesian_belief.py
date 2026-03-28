from typing import Any, Dict

from app.schemas.finance_models import Invoice, Transaction


class BayesianMatcher:
    """Deterministic stub for Bayesian matching confidence."""

    @staticmethod
    def calculate_confidence(transaction: Transaction, invoice: Invoice) -> float:
        """Stub for Bayesian string/date proximity scoring."""
        if transaction.payer_name == invoice.client_name:
            return 0.85
        return 0.50
