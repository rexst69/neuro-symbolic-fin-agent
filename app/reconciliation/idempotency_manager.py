from typing import Set


class IdempotencyManager:
    """Singleton in-memory idempotency lock manager."""

    _instance = None
    _locked_hashes: Set[str] = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def acquire_lock(self, tx_hash: str) -> bool:
        """Acquire a lock for a transaction hash if not already locked."""
        if tx_hash in self._locked_hashes:
            return False

        self._locked_hashes.add(tx_hash)
        return True
