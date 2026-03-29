import json
import random
from datetime import datetime, timezone
import uuid


def generate_mock_bank_feed() -> None:
    """Generate 10 Stripe-like payload rows with one deliberate duplicate for idempotency testing."""
    output_path = "tests/synthetic_data/mock_bank_feed.jsonl"
    lines = []

    base_timestamp = int(datetime.now(timezone.utc).timestamp())

    for index in range(1, 11):
        invoice_ref = f"INV-{index:03d}"
        charge_id = f"ch_{uuid.uuid4().hex[:10]}"
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        amount_cents = random.randint(5000, 15000)

        payload = {
            "id": event_id,
            "amount": amount_cents,
            "currency": "USD",
            "created": base_timestamp + index,
            "description": f"Payment for {invoice_ref}",
            "data": {
                "object": {
                    "id": charge_id,
                    "amount": amount_cents,
                    "currency": "USD",
                    "description": f"Payment for {invoice_ref}",
                    "receipt_email": f"billing{index}@example.com",
                }
            },
        }
        lines.append(json.dumps(payload))

    # Line 5 is a duplicate of line 4 (1-indexed) to validate idempotency locks.
    lines[4] = lines[3]

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    generate_mock_bank_feed()
