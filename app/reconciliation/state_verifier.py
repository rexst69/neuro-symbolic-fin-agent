from app.core.context import AgentContext


class StateVerifier:
    """Mock ERP state verification engine."""

    @staticmethod
    def verify_erp_state(context: AgentContext) -> bool:
        """Mock verification that ERP state aligns with expected post-execution outcome."""
        context.add_trace("StateVerifier", "Queried ERP. State matches expected outcome.")
        return True
