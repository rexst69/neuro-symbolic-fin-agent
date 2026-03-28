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
