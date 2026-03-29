from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.audit_models import AuditAction, DecisionTrace, LNNProof
from app.schemas.finance_models import Invoice, MatchStatus, Transaction


class AgentContext(BaseModel):
    """
    Unified state object that is passed through the pipeline.
    Represents the full context of a transaction's reconciliation lifecycle.
    """
    transaction: Transaction
    matched_invoices: List[Invoice] = Field(default_factory=list)
    workflow_state: str = "INIT"
    match_status: MatchStatus = MatchStatus.UNMATCHED
    belief_state: Dict[str, Any] = Field(default_factory=dict)
    edge_flags: List[str] = Field(default_factory=list)
    compliance_proof: Optional[LNNProof] = None
    decision_trace: Optional[DecisionTrace] = None

    @model_validator(mode="after")
    def init_decision_trace(self) -> "AgentContext":
        """Initialize decision_trace with the transaction's ID if not provided."""
        if self.decision_trace is None and self.transaction is not None:
            self.decision_trace = DecisionTrace(transaction_id=self.transaction.id)
        return self

    def add_trace(
        self, 
        step_name: str, 
        action_taken: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Appends a new AuditAction to the decision trace log.
        Implements the append-only log immutability concept for traceability.
        """
        if details is None:
            details = {}
            
        action = AuditAction(
            step_name=step_name,
            action_taken=action_taken,
            timestamp=datetime.now(timezone.utc),
            details=details
        )
        
        # Ensure decision_trace exists before appending
        if self.decision_trace is None:
            self.decision_trace = DecisionTrace(transaction_id=self.transaction.id)
            
        self.decision_trace.actions.append(action)
