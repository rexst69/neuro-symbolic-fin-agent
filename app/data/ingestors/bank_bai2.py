from typing import List

from app.data.event_store import EventStore
from app.data.normalizer import DataNormalizer
from app.schemas.finance_models import Transaction


def ingest_bai2_file(file_content: str) -> List[Transaction]:
    """Store raw BAI2 file content lineage and return normalized Transactions."""
    EventStore().append("fin.bank.raw", {"content": file_content})

    transactions: List[Transaction] = []
    for row in file_content.splitlines():
        if not row.strip():
            continue
        transactions.append(DataNormalizer.normalize_bai2_row(row))

    return transactions
