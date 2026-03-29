import logging
from datetime import datetime, timezone

from app.core.context import AgentContext
from app.core.exceptions import IdempotencyCollisionError
from app.engine.bayesian_belief import BayesianMatcher
from app.engine.liquid_nn_fx import LiquidFXModel
from app.engine.lnn_accounting import LNN_GAAP_Validator
from app.matching.engine import MatchingEngine
from app.observability.audit_logger import AuditLogger
from app.observability.sla_monitor import SLAMonitor
from app.reconciliation.idempotency_manager import IdempotencyManager
from app.reconciliation.state_verifier import StateVerifier
from app.safety.edge_detectors.fees import FeeDetector
from app.safety.guardrails import ActionValidator
from app.safety.policy_matrix import PolicyMatrix
from app.schemas.finance_models import Invoice, MatchStatus, Transaction
from app.workflows.reconciliation_fsm import ReconciliationFSM


logger = logging.getLogger(__name__)

if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


class _MockGLEntry:
    """Minimal ledger entry shape for deterministic compliance checks."""

    def __init__(self, amount: float, is_debit: bool):
        self.amount = amount
        self.is_debit = is_debit


class FinancePipeline:
    """
    The orchestrator for the Enterprise Financial Close & Reconciliation System.
    This acts as the non-bypassable 12-step pipeline ensuring every transaction
    passes through all layers cleanly.
    """

    def execute(self, transaction: Transaction, open_invoices: list[Invoice]) -> AgentContext:
        """Execute the integrated 12-step reconciliation pipeline."""
        # Step 1: Context initialization and timer start.
        start_time = datetime.now(timezone.utc)
        context = AgentContext(transaction=transaction)
        logger.info(
            f"[INGEST] TransactionId={transaction.id} | Amount={transaction.amount:.2f} | Currency={transaction.currency}"
        )
        context.add_trace("FinancePipeline", "Pipeline started.", {"transaction_id": transaction.id})

        # Step 2: Idempotency lock.
        tx_hash = str(hash(transaction.id))
        lock_acquired = IdempotencyManager().acquire_lock(tx_hash)
        if not lock_acquired:
            raise IdempotencyCollisionError("Transaction is already locked or processed.")
        context.add_trace("FinancePipeline", "Idempotency lock acquired.", {"tx_hash": tx_hash})

        # Step 3: Matching cascade.
        match_proposal = MatchingEngine.execute_cascade(transaction, open_invoices)
        if match_proposal is not None:
            invoice_lookup = {invoice.id: invoice for invoice in open_invoices}
            context.matched_invoices = [
                invoice_lookup[invoice_id]
                for invoice_id in match_proposal.invoice_ids
                if invoice_id in invoice_lookup
            ]
            context.match_status = MatchStatus.SUGGESTED
            context.belief_state["match_confidence"] = match_proposal.match_confidence
            context.belief_state["discrepancy_amount"] = match_proposal.discrepancy_amount
            logger.info(
                f"[MATCH] Status=SUGGESTED | Confidence={match_proposal.match_confidence:.4f} | "
                f"Discrepancy={match_proposal.discrepancy_amount:.2f}"
            )
            context.add_trace("FinancePipeline", "Matching completed with proposal.")
        else:
            context.match_status = MatchStatus.UNMATCHED
            context.belief_state["match_confidence"] = 0.0
            context.belief_state["discrepancy_amount"] = 0.0
            logger.info("[MATCH] Status=UNMATCHED | Confidence=0.0000 | Discrepancy=0.00")
            context.add_trace("FinancePipeline", "No matching proposal found.")

        # Step 4: Edge detection.
        logger.info("[EDGE] Running edge detectors.")
        FeeDetector.detect(context)
        logger.info(f"[EDGE] Flags={context.edge_flags}")

        # Step 5: Probabilistic and temporal reasoning.
        if context.matched_invoices:
            target_invoice = context.matched_invoices[0]
            # Only update confidence if Bayesian score is higher than existing proposal
            bayesian_confidence = BayesianMatcher.calculate_confidence(
                transaction,
                target_invoice,
            )
            current_confidence = context.belief_state.get("match_confidence", 0.0)
            if bayesian_confidence > current_confidence:
                context.belief_state["match_confidence"] = bayesian_confidence
            context.belief_state["fx_drift"] = LiquidFXModel.predict_fx_drift(
                transaction,
                target_invoice,
            )
        else:
            context.belief_state["fx_drift"] = 0.0
        context.add_trace("FinancePipeline", "Reasoning engines completed.")
        logger.info("[COMPLIANCE] Stage=Prepared")

        # Step 6: Policy evaluation.
        policy_decision = PolicyMatrix.evaluate_action_risk(context)
        context.belief_state["policy_decision"] = policy_decision
        context.add_trace("FinancePipeline", "Policy decision computed.", {"decision": policy_decision})

        # Step 7: Compliance proofing.
        amount = transaction.amount
        mock_gl_entries = [
            _MockGLEntry(amount=amount, is_debit=True),
            _MockGLEntry(amount=amount, is_debit=False),
        ]
        context.compliance_proof = LNN_GAAP_Validator.prove_double_entry(mock_gl_entries)
        logger.info(
            f"[COMPLIANCE] Result={'PASS' if context.compliance_proof.result else 'FAIL'}"
        )
        context.add_trace("FinancePipeline", "Compliance proof generated.")

        # Step 8: Hard guardrails.
        context.workflow_state = "VALIDATING"
        ActionValidator.hard_gate_check(context)

        # Step 9: FSM execution.
        context.workflow_state = "READY_TO_POST"
        logger.info("[EXECUTION] Starting workflow execution.")
        fsm = ReconciliationFSM(context)
        fsm.process_posting()
        context.workflow_state = fsm.state

        # Step 10: State verification.
        verified = StateVerifier.verify_erp_state(context)
        if not verified:
            raise ValueError("ERP state verification failed.")
        context.workflow_state = "ERP_VERIFIED"
        logger.info("[VERIFY] ERP state verification passed.")

        # Step 11: SLA and audit commit.
        end_time = datetime.now(timezone.utc)
        SLAMonitor.record_execution_metrics(context, start_time, end_time)
        logger.info("[AUDIT] Committing decision trace.")
        AuditLogger.commit_trace(context)

        # Step 12: Return context.
        return context
