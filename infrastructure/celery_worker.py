import os

from celery import Celery

from app.core.pipeline import FinancePipeline
from app.schemas.finance_models import Transaction

celery_app = Celery("fin_tasks", broker="redis://localhost:6379/0")
os.environ.setdefault("FIN_AGENT_ENV", "local")


@celery_app.task
def process_transaction_task(raw_payload: dict) -> str:
    """Parse a raw payload into a Transaction and process it through the pipeline."""
    transaction = Transaction(
        id=str(raw_payload.get("id", "txn_unknown")),
        amount=float(raw_payload.get("amount", 0.0)),
        currency=str(raw_payload.get("currency", "USD")).upper(),
        date=raw_payload.get("date", "1970-01-01T00:00:00Z"),
        reference=str(raw_payload.get("reference", "")),
        type=str(raw_payload.get("type", "PAYMENT")).upper(),
        payer_name=raw_payload.get("payer_name"),
        raw_source_id=raw_payload.get("raw_source_id"),
    )

    context = FinancePipeline().execute(transaction, [])
    return context.workflow_state
