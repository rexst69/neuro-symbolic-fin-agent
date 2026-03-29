from typing import Any, Dict, Optional


class FinanceAgentError(Exception):
    """Base exception for all errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class IdempotencyCollisionError(FinanceAgentError):
    """Raised when a transaction hash is already locked or processed."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ExternalStateMismatchError(FinanceAgentError):
    """Raised during reconciliation when the ERP/external state doesn't match the expected local state."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ComplianceHaltError(FinanceAgentError):
    """Raised when the Symbolic LNN rules (GAAP/Accounting constraints) explicitly fail and return FALSE."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class RiskEscalationError(FinanceAgentError):
    """Raised when probabilistic confidence is too low or transaction amount exceeds autonomous threshold."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class TransitionError(FinanceAgentError):
    """Raised by the FSM when an invalid state transition is attempted."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class TransitionExecutionError(FinanceAgentError):
    """Raised when a transition forward action fails after retries."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class RecoveryHaltError(FinanceAgentError):
    """Raised to halt pipeline execution after a successful compensating rollback."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class RecoveryRollbackFailedError(FinanceAgentError):
    """Raised when compensating rollback execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class MissingRollbackActionError(FinanceAgentError):
    """Raised when a failed forward transition has no rollback action defined."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ExecutionDispatchError(FinanceAgentError):
    """Raised when the execution dispatcher cannot route or execute an action."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
