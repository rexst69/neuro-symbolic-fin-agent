from typing import Any, Dict

from fastapi import FastAPI

from app.core.pipeline import FinancePipeline
from app.data.ingestors.webhook_stripe import ingest_stripe_event

app = FastAPI()


@app.post("/api/v1/webhooks/stripe")
def stripe_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
	"""Accept a Stripe webhook, normalize it, and run the finance pipeline."""
	transaction = ingest_stripe_event(payload)
	open_invoices = []
	context = FinancePipeline().execute(transaction, open_invoices)

	return {
		"status": "success",
		"transaction_id": context.transaction.id,
		"workflow_state": context.workflow_state,
	}
