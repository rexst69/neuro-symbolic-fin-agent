import logging
from typing import List

from app.schemas.audit_models import LNNProof
from app.schemas.finance_models import GL_Entry


logger = logging.getLogger(__name__)


class LNN_GAAP_Validator:
    """Deterministic GAAP validator for symbolic double-entry accounting checks."""

    @staticmethod
    def prove_double_entry(proposed_gl_entries: List[GL_Entry]) -> LNNProof:
        """Prove whether proposed ledger entries satisfy GAAP double-entry balance."""
        total_debits = sum(entry.amount for entry in proposed_gl_entries if entry.is_debit)
        total_credits = sum(entry.amount for entry in proposed_gl_entries if not entry.is_debit)

        rounded_debits = round(total_debits, 2)
        rounded_credits = round(total_credits, 2)
        is_balanced = rounded_debits == rounded_credits
        valid = is_balanced

        logger.info(f"[COMPLIANCE] DoubleEntryCheck={'PASS' if valid else 'FAIL'}")

        debit_entries = [round(entry.amount, 2) for entry in proposed_gl_entries if entry.is_debit]
        credit_entries = [round(entry.amount, 2) for entry in proposed_gl_entries if not entry.is_debit]
        if len(debit_entries) >= 2 and credit_entries:
            logger.info(
                f"[COMPLIANCE] Equation: Debit({debit_entries[0]:.2f}) + "
                f"Debit({debit_entries[1]:.2f}) == Credit({credit_entries[0]:.2f})"
            )
        elif debit_entries and credit_entries:
            logger.info(
                f"[COMPLIANCE] Equation: Debit({debit_entries[0]:.2f}) "
                f"== Credit({credit_entries[0]:.2f})"
            )

        if is_balanced:
            logic_trace = (
                "FORALL x IN GL_Entries: "
                f"SUM(Debits) [{rounded_debits:.2f}] EQUIV "
                f"SUM(Credits) [{rounded_credits:.2f}] |- TRUE"
            )
        else:
            delta = round(rounded_debits - rounded_credits, 2)
            logic_trace = (
                "FORALL x IN GL_Entries: "
                f"SUM(Debits) [{rounded_debits:.2f}] NOT_EQ "
                f"SUM(Credits) [{rounded_credits:.2f}] "
                f"(DELTA={delta:.2f}) |- FALSE"
            )

        rules_evaluated = ["GAAP_DOUBLE_ENTRY_BALANCE"]

        return LNNProof(
            result=is_balanced,
            logic_trace=logic_trace,
            rules_evaluated=rules_evaluated,
        )
