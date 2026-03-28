from typing import Any, Dict

from app.core.context import AgentContext
from app.execution.erp_connectors.netsuite_rest import NetSuiteConnector


class ExecutionDispatcher:
    """Dispatches execution actions to mocked ERP connectors and records traces."""

    @staticmethod
    def dispatch(action: str, payload: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute a supported action and append success/failure traces to context."""
        try:
            if action == "POST_JE":
                result = NetSuiteConnector.post_journal_entry(payload)
            elif action == "REVERSE_JE":
                result = NetSuiteConnector.reverse_journal_entry(payload["internal_id"])
            else:
                raise ValueError("Unknown execution action.")

            context.add_trace("ExecutionDispatcher", f"Successfully executed API: {action}")
            return result
        except Exception as e:
            context.add_trace("ExecutionDispatcher", f"API Execution Failed: {str(e)}")
            raise
