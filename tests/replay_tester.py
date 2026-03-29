import json
import os
import sys
from datetime import datetime, timezone

# Ensure the root directory is on the path so 'app' can be imported easily
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.pipeline import FinancePipeline
from app.data.normalizer import DataNormalizer
from app.schemas.finance_models import Invoice


def create_sample_invoices(input_path: str) -> list[Invoice]:
    """Create sample invoices by inspecting the synthetic payload to ensure perfectly matching amounts."""
    invoices = []
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                amount = float(data["amount"]) / 100.0  # Stripe cents to dollars
                
                # Extract invoice ID from description, fallback generic if not found
                desc = data["data"]["object"]["description"]
                invoice_id = desc.split("for ")[-1] if "for " in desc else f"INV-{len(invoices)+1:03d}"
                
                # Check if we already created this invoice (for duplicate handling)
                if not any(inv.id == invoice_id for inv in invoices):
                    invoices.append(
                        Invoice(
                            id=invoice_id,
                            total_amount=amount,
                            balance_due=amount,
                            currency="USD",
                            issue_date=datetime.now(timezone.utc),
                            due_date=datetime.now(timezone.utc),
                            client_name="ACME Corp",
                            status="OPEN",
                        )
                    )
    except FileNotFoundError:
        pass
    return invoices


def run_replay() -> None:
    """Replay synthetic payloads through normalization and pipeline execution."""
    input_path = "tests/synthetic_data/mock_bank_feed.jsonl"
    pipeline = FinancePipeline()
    open_invoices = create_sample_invoices(input_path)

    with open(input_path, "r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue

            payload = json.loads(raw_line)

            try:
                transaction = DataNormalizer.normalize_stripe_webhook(payload)
                context = pipeline.execute(transaction, open_invoices)

                if hasattr(context.decision_trace, "model_dump"):
                    trace_output = context.decision_trace.model_dump()
                else:
                    trace_output = context.decision_trace.dict()

                print(f"[ROW {line_number}] workflow_state={context.workflow_state}")
                print(f"[ROW {line_number}] decision_trace={json.dumps(trace_output, default=str)}")
            except Exception as exc:
                if type(exc).__name__ == "IdempotencyCollisionError":
                    print(
                        f"[ROW {line_number}] Expected duplicate detected. "
                        "Idempotency lock worked."
                    )
                else:
                    print(f"[ROW {line_number}] Error: {exc}")


if __name__ == "__main__":
    run_replay()
