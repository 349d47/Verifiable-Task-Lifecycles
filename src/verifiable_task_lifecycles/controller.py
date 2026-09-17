from __future__ import annotations

from dataclasses import dataclass, field

from .canonical import content_id
from .model import Action, AcceptedTransition, Evidence, Intent, Payment, TaskState
from .policy import Decision, PolicyEvaluator


@dataclass
class TaskContext:
    instance_id: str
    intent: Intent
    state: TaskState = TaskState.ACTIVE
    history: list[AcceptedTransition] = field(default_factory=list)


class LifecycleController:
    """Deterministic admission/binding core separated from planning and payment transports."""

    def __init__(self, evaluator: PolicyEvaluator):
        self.evaluator = evaluator
        self._settlements: set[str] = set()

    def admit(self, context: TaskContext, action: Action) -> tuple[Decision, str]:
        return self.evaluator.evaluate(context.intent, context.state, context.history, action)

    def validate_binding(self, context: TaskContext, action: Action, payment: Payment, evidence: Evidence) -> list[str]:
        issues: list[str] = []
        aid = content_id(action.as_artifact())
        if payment.action_id != aid:
            issues.append("Payment.action_id mismatch")
        if evidence.action_id != aid:
            issues.append("Evidence.action_id mismatch")
        if evidence.instance_id != context.instance_id:
            issues.append("Evidence.instance_id mismatch")
        if payment.payee != action.provider:
            issues.append("Payment.payee mismatch")
        if payment.amount != action.value:
            issues.append("Payment.amount mismatch")
        if evidence.receipt_ref is not None and evidence.receipt_ref != payment.reference:
            issues.append("Evidence.receipt_ref mismatch")
        if payment.reference in self._settlements:
            issues.append("settlement reference reused")
        return issues

    def accept(self, context: TaskContext, action: Action, payment: Payment, evidence: Evidence) -> None:
        decision, reason = self.admit(context, action)
        if decision is not Decision.PERMIT:
            raise ValueError(f"action denied: {reason}")
        issues = self.validate_binding(context, action, payment, evidence)
        if issues:
            raise ValueError("; ".join(issues))
        self._settlements.add(payment.reference)
        context.history.append(AcceptedTransition(action, payment, evidence))

    @staticmethod
    def finalize(context: TaskContext, final_state: TaskState) -> None:
        if context.state is not TaskState.ACTIVE:
            raise ValueError("task already terminal")
        if not final_state.terminal:
            raise ValueError("final state must be Completed, Failed, or Revoked")
        context.state = final_state
