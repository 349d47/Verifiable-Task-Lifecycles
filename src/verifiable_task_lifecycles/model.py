from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class TaskState(IntEnum):
    NONE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3
    REVOKED = 4

    @classmethod
    def from_name(cls, value: str) -> "TaskState":
        return cls[value.strip().upper()]

    @property
    def wire_name(self) -> str:
        return self.name.lower()

    @property
    def terminal(self) -> bool:
        return self in {self.COMPLETED, self.FAILED, self.REVOKED}


@dataclass(frozen=True)
class Intent:
    goal: str
    budget: int
    allowed_services: tuple[str, ...]
    allowed_providers: tuple[str, ...]

    def as_artifact(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "budget": self.budget,
            "allowed_services": list(self.allowed_services),
            "allowed_providers": list(self.allowed_providers),
        }


@dataclass(frozen=True)
class ActionProposal:
    """Planner-controlled fields only. Economic terms are resolved from a trusted catalog."""
    service: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    operation: str
    provider: str
    service: str
    parameters: dict[str, Any]
    value: int

    def as_artifact(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "provider": self.provider,
            "service": self.service,
            "parameters": self.parameters,
            "value": self.value,
        }


@dataclass(frozen=True)
class Payment:
    reference: str
    payer: str
    payee: str
    amount: int
    action_id: str
    protocol: str
    network: str

    def as_artifact(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "payer": self.payer,
            "payee": self.payee,
            "amount": self.amount,
            "action_id": self.action_id,
            "protocol": self.protocol,
            "network": self.network,
        }


@dataclass(frozen=True)
class Evidence:
    instance_id: str
    action_id: str
    result: str
    outcome: str
    receipt_ref: str | None = None

    def as_artifact(self) -> dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "action_id": self.action_id,
            "result": self.result,
            "outcome": self.outcome,
            "receipt_ref": self.receipt_ref,
        }


@dataclass(frozen=True)
class TransitionRecord:
    instance_id: str
    transition_no: int
    previous_state: str
    action_id: str
    payment_id: str
    evidence_id: str
    next_state: str


@dataclass(frozen=True)
class AcceptedTransition:
    action: Action
    payment: Payment
    evidence: Evidence
    previous_state: TaskState = TaskState.ACTIVE
    next_state: TaskState = TaskState.ACTIVE
