import json
from typing import Any, Dict

from app.core.context import AgentContext


class AuditLogger:
    """Simulated write-once audit logger for decision traces."""

    @staticmethod
    def commit_trace(context: AgentContext) -> None:
        """Append the current decision trace as JSON to a local JSONL ledger."""
        trace = context.decision_trace

        if trace is None:
            trace_json = json.dumps(
                {
                    "transaction_id": context.transaction.id,
                    "actions": [],
                }
            )
        elif hasattr(trace, "model_dump_json"):
            trace_json = trace.model_dump_json()
        else:
            trace_dict: Dict[str, Any] = trace.dict()
            trace_json = json.dumps(trace_dict)

        with open("audit_ledger.jsonl", "a", encoding="utf-8") as ledger:
            ledger.write(trace_json + "\n")
