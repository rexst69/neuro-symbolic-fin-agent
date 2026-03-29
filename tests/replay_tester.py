import json
from datetime import datetime

from app.core.pipeline import FinancePipeline
from app.data.normalizer import DataNormalizer
from app.schemas.finance_models import Invoice


def create_sample_invoices() -> list[Invoice]:
    """Create sample invoices for matching."""
    return [
        Invoice(
            id="INV-001",
            total_amount=121.0,
            balance_due=121.0,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-002",
            total_amount=55.09,
            balance_due=55.09,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-003",
            total_amount=107.75,
            balance_due=107.75,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-004",
            total_amount=104.92,
            balance_due=104.92,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-006",
            total_amount=66.26,
            balance_due=66.26,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-007",
            total_amount=95.85,
            balance_due=95.85,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-008",
            total_amount=137.8,
            balance_due=137.8,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-009",
            total_amount=118.05,
            balance_due=118.05,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
        Invoice(
            id="INV-010",
            total_amount=85.97,
            balance_due=85.97,
            currency="USD",
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            client_name="ACME Corp",
            status="OPEN",
        ),
    ]


def run_replay() -> None:
    """Replay synthetic payloads through normalization and pipeline execution."""
    input_path = "tests/synthetic_data/mock_bank_feed.jsonl"
    pipeline = FinancePipeline()
    open_invoices = create_sample_invoices()

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
                print(f"[ROW {line_number}] decision_trace={trace_output}")
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
