from typing import Any, Dict


class NetSuiteConnector:
    """Mock NetSuite REST connector for journal posting and reversal operations."""

    @staticmethod
    def post_journal_entry(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock posting a journal entry to NetSuite."""
        return {
            "status": "success",
            "internal_id": "JE-9999",
            "message": "Successfully posted to NetSuite.",
        }

    @staticmethod
    def reverse_journal_entry(internal_id: str) -> Dict[str, Any]:
        """Mock reversing a previously posted journal entry in NetSuite."""
        return {
            "status": "success",
            "reversal_id": "JE-10000",
            "message": f"Successfully reversed {internal_id}.",
        }
