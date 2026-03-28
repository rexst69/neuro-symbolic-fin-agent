# SYSTEM DIRECTIVES FOR COPILOT

You are building an Enterprise Finance Reconciliation System. 
Adhere to these absolute invariants:
1. NO generic `Exception` throwing for flow control. Use specific errors (e.g., `IdempotencyError`).
2. NO database connections in the Data Layer or Observability Layer.
3. ALL state and data must flow strictly through the `AgentContext` Pydantic object.
4. NO external API calls outside of the `app/execution/` directory.
5. In workflows, EVERY forward action MUST have a defined `rollback_action` (Reverse Journal Entry).
6. Never write SQL. Assume an Event Sourcing architecture (append-only).
