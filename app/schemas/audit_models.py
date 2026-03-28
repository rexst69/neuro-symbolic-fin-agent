from datetime import datetime
from typing import List, Dict, Any

from pydantic import BaseModel, Field


class LNNProof(BaseModel):
    """
    Logical Neural Network (LNN) Proof detailing the evaluation 
    of GAAP or accounting rules for a transaction.
    """
    result: bool
    logic_trace: str
    rules_evaluated: List[str]


class AuditAction(BaseModel):
    """
    Represents an audit log entry for a specific action taken 
    by the system during financial reconciliation.
    """
    step_name: str
    action_taken: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any]


class DecisionTrace(BaseModel):
    """
    A comprehensive trace of all system decisions and actions 
    made for a particular financial transaction.
    """
    transaction_id: str
    actions: List[AuditAction] = Field(default_factory=list)
