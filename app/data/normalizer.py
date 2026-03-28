from datetime import datetime, timezone
from typing import Any, Dict

from app.schemas.finance_models import Currency, Transaction, TransactionType


class DataNormalizer:
    """
    Pure functions to coerce messy external payloads into strict internal Pydantic models.
    """

    @staticmethod
    def normalize_stripe_webhook(payload: Dict[str, Any]) -> Transaction:
        """
        Normalizes a standard Stripe charge.succeeded webhook payload into a Transaction.
        """
        try:
            obj = payload["data"]["object"]
            transaction_id = str(obj["id"])
            amount = float(obj["amount"]) / 100.0
            currency = Currency(str(obj["currency"]).strip().upper())
            date = datetime.fromtimestamp(float(payload["created"]), tz=timezone.utc)
            reference = str(obj.get("description") or "")
            payer_name_raw = obj.get("receipt_email")
            payer_name = str(payer_name_raw) if payer_name_raw is not None else None
            raw_source_id = str(payload["id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid Stripe payload: {exc}") from exc

        if amount < 0:
            raise ValueError("Invalid Stripe payload: amount must be non-negative.")

        return Transaction(
            id=transaction_id,
            amount=amount,
            currency=currency,
            date=date,
            reference=reference,
            type=TransactionType.PAYMENT,
            payer_name=payer_name,
            raw_source_id=raw_source_id,
        )

    @staticmethod
    def normalize_bai2_row(row: str) -> Transaction:
        """
        Normalizes a mock BAI2 bank file CSV row into a Transaction.
        Format expected: Date(YYYY-MM-DD),Amount,Currency,Ref,Type
        """
        if not isinstance(row, str) or not row.strip():
            raise ValueError("Invalid BAI2 row: row must be a non-empty string.")

        parts = [part.strip() for part in row.split(",")]
        if len(parts) != 5:
            raise ValueError(f"Invalid BAI2 row: expected 5 columns, got {len(parts)}.")

        date_text, amount_text, currency_text, reference, type_text = parts

        try:
            date = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            signed_amount = float(amount_text)
            currency = Currency(currency_text.upper())
        except ValueError as exc:
            raise ValueError(f"Invalid BAI2 row: {exc}") from exc

        normalized_type = type_text.upper()
        if signed_amount > 0:
            transaction_type = TransactionType.PAYMENT
        elif signed_amount < 0:
            # The schema does not define FEE, so negative fee-like entries map to CHARGEBACK.
            if normalized_type in {"FEE", "CHARGEBACK"}:
                transaction_type = TransactionType.CHARGEBACK
            elif normalized_type in TransactionType._value2member_map_:
                transaction_type = TransactionType(normalized_type)
            else:
                transaction_type = TransactionType.CHARGEBACK
        else:
            if normalized_type in TransactionType._value2member_map_:
                transaction_type = TransactionType(normalized_type)
            else:
                transaction_type = TransactionType.ADJUSTMENT

        transaction_id = f"bai2_{abs(hash(row))}"

        return Transaction(
            id=transaction_id,
            amount=abs(signed_amount),
            currency=currency,
            date=date,
            reference=reference,
            type=transaction_type,
            payer_name=None,
            raw_source_id=None,
        )
