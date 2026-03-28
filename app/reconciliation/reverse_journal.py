from app.core.context import AgentContext


class CompensatingActionEngine:
    """Mock compensating action engine for rollback execution."""

    @staticmethod
    def execute_rollback(context: AgentContext) -> bool:
        """Generate and post a reverse journal entry as a rollback action."""
        context.add_trace("CompensatingActionEngine", "Reverse Journal Entry generated and posted.")
        return True
