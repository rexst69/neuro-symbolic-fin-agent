from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict

from app.core.context import AgentContext
from app.core.exceptions import (
    IdempotencyCollisionError,
    MissingRollbackActionError,
    RecoveryHaltError,
    RecoveryRollbackFailedError,
    TransitionError,
    TransitionExecutionError,
)


class Transition(BaseModel):
    """
    Defines a state transition in the ResilientFSM.
    Contains the forward execution action and an optional rollback action.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    from_state: str
    to_state: str
    forward_action: Callable[[AgentContext], Any]
    rollback_action: Optional[Callable[[AgentContext], Any]] = None
    max_retries: int = 3


class ResilientFSM:
    """
    The base state machine that all financial workflows will inherit from.
    Enforces retries, error handling, and reverse journal entries (rollbacks).
    """

    def __init__(self, context: AgentContext, initial_state: str = "INIT"):
        self.context = context
        self.state = initial_state

    def execute_transition(self, transition: Transition) -> Any:
        """
        Executes a transition with strict retry policies and idempotency checks.
        """
        if self.state != transition.from_state:
            raise TransitionError(
                "Invalid state transition.",
                details={
                    "current_state": self.state,
                    "expected_from_state": transition.from_state,
                    "to_state": transition.to_state,
                },
            )

        attempts = 0
        last_error: Optional[Exception] = None
        while attempts < transition.max_retries:
            attempts += 1
            try:
                # Try executing the forward action
                result = transition.forward_action(self.context)

                # Execution successful
                self.state = transition.to_state
                self.context.add_trace(
                    step_name=f"FSM Transition: {transition.from_state} -> {transition.to_state}",
                    action_taken="SUCCESS",
                    details={"attempt": attempts}
                )
                return result

            except IdempotencyCollisionError as e:
                # Do not retry on an idempotency lock/collision error
                self.context.add_trace(
                    step_name=f"FSM Transition: {transition.from_state} -> {transition.to_state}",
                    action_taken="IDEMPOTENCY_COLLISION",
                    details={"error": str(e), "attempt": attempts}
                )
                self.state = "LOCKED"
                raise e

            except Exception as e:
                # Log the temporary failure and allow loop to retry
                last_error = e
                self.context.add_trace(
                    step_name=f"FSM Transition: {transition.from_state} -> {transition.to_state}",
                    action_taken="FAILURE_ATTEMPT",
                    details={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "attempt": attempts,
                    },
                )

        # Loop exhausted max_retries
        self.state = "PARTIALLY_EXECUTED"
        self._trigger_recovery(transition, last_error)

        # This line is unreachable because recovery always raises a terminal exception.
        raise TransitionExecutionError(
            "Transition exhausted retries and failed recovery path unexpectedly.",
            details={"from_state": transition.from_state, "to_state": transition.to_state},
        )

    def _trigger_recovery(self, transition: Transition, last_error: Optional[Exception]) -> None:
        """
        Attempts to execute the compensating action to rollback the state.
        Raises an exception upon completion to halt execution.
        """
        self.state = "RECOVERY_IN_PROGRESS"
        self.context.add_trace(
            step_name=f"Recovery: {transition.from_state} -> {transition.to_state}",
            action_taken="RECOVERY_STARTED",
            details={"transition_failed": True}
        )

        if transition.rollback_action:
            try:
                transition.rollback_action(self.context)
            except Exception as e:
                self.state = "AWAITING_RECOVERY"
                self.context.add_trace(
                    step_name=f"Recovery: {transition.from_state} -> {transition.to_state}",
                    action_taken="ROLLBACK_FAILED",
                    details={"error": str(e), "error_type": type(e).__name__},
                )
                raise RecoveryRollbackFailedError(
                    "Manual intervention required. Rollback action failed.",
                    details={
                        "from_state": transition.from_state,
                        "to_state": transition.to_state,
                        "triggering_error": str(last_error) if last_error else None,
                    },
                ) from e

            self.state = "FAILURE_RECONCILED"
            self.context.add_trace(
                step_name=f"Recovery: {transition.from_state} -> {transition.to_state}",
                action_taken="ROLLBACK_SUCCESS",
                details={
                    "info": "Rollback function securely reversed standard execution.",
                    "triggering_error": str(last_error) if last_error else None,
                },
            )
            raise RecoveryHaltError(
                "Pipeline halted gracefully. Execution failed but state was successfully rolled back.",
                details={
                    "from_state": transition.from_state,
                    "to_state": transition.to_state,
                    "attempts_exhausted": True,
                },
            )
        else:
            self.state = "AWAITING_RECOVERY"
            self.context.add_trace(
                step_name=f"Recovery: {transition.from_state} -> {transition.to_state}",
                action_taken="NO_ROLLBACK_ACTION_DEFINED",
                details={
                    "triggering_error": str(last_error) if last_error else None,
                },
            )
            raise MissingRollbackActionError(
                "Manual intervention required. No compensating rollback action was defined.",
                details={
                    "from_state": transition.from_state,
                    "to_state": transition.to_state,
                },
            )
