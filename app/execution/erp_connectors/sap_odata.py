from typing import Any, Dict


class SAPConnector:
    """Mock SAP OData connector for journal post and reversal actions."""

    @staticmethod
    def post_journal_entry(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock a successful SAP OData journal posting response."""
        return {"d": {"results": "success", "DocumentNo": "SAP-1234"}}

    @staticmethod
    def reverse_journal_entry(document_no: str) -> Dict[str, Any]:
        """Mock a successful SAP OData journal reversal response."""
        return {
            "d": {
                "results": "success",
                "ReversalDocumentNo": "SAP-1235",
                "message": f"Successfully reversed {document_no}.",
            }
        }
