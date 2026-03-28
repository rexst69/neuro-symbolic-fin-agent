from typing import Any, Dict

from app.data.event_store import EventStore
from app.data.normalizer import DataNormalizer
from app.schemas.finance_models import Transaction


def ingest_stripe_event(payload: Dict[str, Any]) -> Transaction:
    """Store raw Stripe payload lineage and return a normalized Transaction."""
    EventStore().append("fin.stripe.raw", payload)
    transaction = DataNormalizer.normalize_stripe_webhook(payload)
    return transaction
