from datetime import datetime

import pytest

from app.core.context import AgentContext
from app.core.exceptions import ComplianceHaltError
from app.engine.lnn_accounting import LNN_GAAP_Validator
from app.safety.guardrails import ActionValidator
from app.schemas.audit_models import LNNProof
from app.schemas.finance_models import Currency, GL_Entry, Transaction, TransactionType


def test_lnn_gaap_balanced() -> None:
    debit_entry = GL_Entry(
        account_code="1000",
        amount=100.0,
        is_debit=True,
        description="Debit leg",
        transaction_id="txn_balanced",
    )
    credit_entry = GL_Entry(
        account_code="2000",
        amount=100.0,
        is_debit=False,
        description="Credit leg",
        transaction_id="txn_balanced",
    )

    proof = LNN_GAAP_Validator.prove_double_entry([debit_entry, credit_entry])

    assert proof.result is True


def test_lnn_gaap_unbalanced() -> None:
    debit_entry = GL_Entry(
        account_code="1000",
        amount=100.0,
        is_debit=True,
        description="Debit leg",
        transaction_id="txn_unbalanced",
    )
    credit_entry = GL_Entry(
        account_code="2000",
        amount=99.0,
        is_debit=False,
        description="Credit leg",
        transaction_id="txn_unbalanced",
    )

    proof = LNN_GAAP_Validator.prove_double_entry([debit_entry, credit_entry])

    assert proof.result is False


def test_guardrail_halts_on_failed_compliance() -> None:
    transaction = Transaction(
        id="txn_guardrail",
        amount=100.0,
        currency=Currency.USD,
        date=datetime.utcnow(),
        reference="INV-100",
        type=TransactionType.PAYMENT,
        payer_name="Acme Corp",
        raw_source_id="evt_guardrail",
    )

    context = AgentContext(transaction=transaction)
    context.workflow_state = "VALIDATING"
    context.belief_state["policy_decision"] = "DETERMINISTIC_ALLOW"
    context.compliance_proof = LNNProof(
        result=False,
        logic_trace="Failed",
        rules_evaluated=[],
    )

    with pytest.raises(ComplianceHaltError):
        ActionValidator.hard_gate_check(context)
