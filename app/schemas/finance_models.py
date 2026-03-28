from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class Currency(str, Enum):
    """Supported currencies in the Enterprise system."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"


class MatchStatus(str, Enum):
    """Status lifecycle of a transaction match."""
    UNMATCHED = "UNMATCHED"
    SUGGESTED = "SUGGESTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    READY_TO_POST = "READY_TO_POST"
    POSTED = "POSTED"
    ERP_VERIFIED = "ERP_VERIFIED"
    RECON_FAILED = "RECON_FAILED"


class TransactionType(str, Enum):
    """Categorization of financial transactions."""
    PAYMENT = "PAYMENT"
    INVOICE = "INVOICE"
    CREDIT_NOTE = "CREDIT_NOTE"
    ADJUSTMENT = "ADJUSTMENT"
    CHARGEBACK = "CHARGEBACK"


class Transaction(BaseModel):
    """Represents a financial transaction in the system."""
    id: str
    amount: float = Field(..., ge=0)
    currency: Currency
    date: datetime
    reference: str
    type: TransactionType
    payer_name: Optional[str] = None
    raw_source_id: Optional[str] = None


class Invoice(BaseModel):
    """Represents an invoice issued to a client."""
    id: str
    total_amount: float = Field(..., ge=0)
    balance_due: float = Field(..., ge=0)
    currency: Currency
    issue_date: datetime
    due_date: datetime
    client_name: str
    status: str


class GL_Entry(BaseModel):
    """Represents a single General Ledger entry."""
    account_code: str
    amount: float = Field(..., ge=0)
    is_debit: bool
    description: str
    transaction_id: str


class MatchProposal(BaseModel):
    """Represents a proposed match between a transaction and one or more invoices."""
    transaction_id: str
    invoice_ids: List[str]
    match_confidence: float = Field(..., ge=0.0, le=1.0)
    discrepancy_amount: float
    match_type: str
