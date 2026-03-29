from datetime import datetime
from typing import Any, Dict

from app.core.context import AgentContext


class SLAMonitor:
    """Records simple execution latency metrics for transaction processing."""

    @staticmethod
    def record_execution_metrics(context: AgentContext, start_time: datetime, end_time: datetime) -> None:
        """Compute and emit an execution duration metric for the current transaction."""
        duration = (end_time - start_time).total_seconds()
        print(
            f"[METRICS] Transaction {context.transaction.id} processed in {duration} seconds. "
            f"State: {context.workflow_state}"
        )
