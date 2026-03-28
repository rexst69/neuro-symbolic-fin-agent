from app.core.context import AgentContext
from app.core.exceptions import ComplianceHaltError, RiskEscalationError


class ActionValidator:
    """Final hard-gate validator before external execution can be attempted."""

    @staticmethod
    def hard_gate_check(context: AgentContext) -> bool:
        """Enforce compliance, policy, and workflow-state checks with fail-fast behavior."""
        if context.compliance_proof is None or context.compliance_proof.result is False:
            raise ComplianceHaltError("GAAP validation failed or missing.")

        policy_decision = context.belief_state.get("policy_decision")
        if policy_decision == "ESCALATE_TO_HUMAN":
            raise RiskEscalationError("Transaction exceeds autonomous risk thresholds.")

        if context.workflow_state != "VALIDATING":
            raise ValueError("Invalid workflow state for execution gating.")

        context.add_trace("ActionValidator", "All hard gates passed. Ready for execution.")
        return True
