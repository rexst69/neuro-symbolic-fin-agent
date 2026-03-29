from typing import Any, Dict

from app.core.context import AgentContext
from app.core.exceptions import ExecutionDispatchError
from app.execution.erp_connectors.netsuite_rest import NetSuiteConnector
from app.execution.erp_connectors.sap_odata import SAPConnector


class ExecutionDispatcher:
    """Dispatches execution actions to ERP connectors and records traces."""

    @staticmethod
    def _resolve_connector(context: AgentContext) -> Any:
        target_erp = str(context.belief_state.get("target_erp", "NETSUITE")).upper()
        if target_erp == "NETSUITE":
            return "NETSUITE", NetSuiteConnector
        if target_erp == "SAP":
            return "SAP", SAPConnector

        raise ExecutionDispatchError(
            "Unsupported ERP target.",
            details={"target_erp": target_erp},
        )

    @staticmethod
    def dispatch(action: str, payload: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute a supported action and append traces to context."""
        connector_name, connector = ExecutionDispatcher._resolve_connector(context)

        if action == "POST_JE":
            result = connector.post_journal_entry(payload)
        elif action == "REVERSE_JE":
            journal_id = payload.get("journal_id")
            if not journal_id:
                raise ExecutionDispatchError(
                    "Rollback journal identifier is required.",
                    details={"payload_keys": sorted(payload.keys())},
                )
            result = connector.reverse_journal_entry(journal_id)
        else:
            raise ExecutionDispatchError(
                "Unknown execution action.",
                details={"action": action},
            )

        normalized = {
            "action": action,
            "connector": connector_name,
            "result": result,
        }
        context.add_trace(
            "ExecutionDispatcher",
            "Execution action completed.",
            {"action": action, "connector": connector_name},
        )
        return normalized
