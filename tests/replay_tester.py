import json

from app.core.pipeline import FinancePipeline
from app.data.normalizer import DataNormalizer


def run_replay() -> None:
    """Replay synthetic payloads through normalization and pipeline execution."""
    input_path = "tests/synthetic_data/mock_bank_feed.jsonl"
    pipeline = FinancePipeline()

    with open(input_path, "r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue

            payload = json.loads(raw_line)

            try:
                transaction = DataNormalizer.normalize_stripe_webhook(payload)
                context = pipeline.execute(transaction, [])

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
