from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .model import Action, ActionProposal, AcceptedTransition, Intent, TaskState


class Decision(str, Enum):
    PERMIT = "permit"
    DENY = "deny"


@dataclass(frozen=True)
class CatalogEntry:
    service: str
    provider: str
    value: int
    endpoint: str
    pay_to: str
    equivalence_group: str | None = None


class TrustedCatalog:
    """Resolves planner-selected service names into trusted economic parameters."""

    def __init__(self, entries: Iterable[CatalogEntry]):
        self._by_service = {entry.service: entry for entry in entries}
        if not self._by_service:
            raise ValueError("catalog must contain at least one service")

    def entry(self, service: str) -> CatalogEntry:
        try:
            return self._by_service[service]
        except KeyError as exc:
            raise ValueError(f"unknown service: {service}") from exc

    def resolve(self, proposal: ActionProposal | dict[str, Any]) -> Action:
        if isinstance(proposal, dict):
            allowed = {"service", "parameters"}
            unexpected = set(proposal) - allowed
            if unexpected:
                raise ValueError(
                    "planner proposal attempted to set controller-owned fields: "
                    + ", ".join(sorted(unexpected))
                )
            proposal = ActionProposal(
                service=str(proposal["service"]),
                parameters=dict(proposal.get("parameters", {})),
            )
        entry = self.entry(proposal.service)
        params = dict(proposal.parameters)
        # Endpoint is deliberately controller-owned and is injected after planning.
        params.setdefault("endpoint", entry.endpoint)
        return Action(
            operation="purchase_service",
            provider=entry.provider,
            service=entry.service,
            parameters=params,
            value=entry.value,
        )


class PolicyEvaluator:
    """Deterministic implementation of enabled_M, auth_I, and history-aware Pi."""

    def __init__(self, catalog: TrustedCatalog):
        self.catalog = catalog

    @staticmethod
    def spent(history: Iterable[AcceptedTransition]) -> int:
        return sum(t.payment.amount for t in history)

    def evaluate(
        self,
        intent: Intent,
        state: TaskState,
        history: list[AcceptedTransition],
        action: Action,
    ) -> tuple[Decision, str]:
        if state is not TaskState.ACTIVE:
            return Decision.DENY, "task is terminal"

        if action.provider not in intent.allowed_providers:
            return Decision.DENY, "provider is outside delegated authorization"
        if action.service not in intent.allowed_services:
            return Decision.DENY, "service is outside delegated authorization"

        entry = self.catalog.entry(action.service)
        if action.provider != entry.provider or action.value != entry.value:
            return Decision.DENY, "action economic terms do not match trusted catalog"

        if self.spent(history) + action.value > intent.budget:
            return Decision.DENY, "task budget would be exceeded"

        group = entry.equivalence_group or entry.service
        for prior in history:
            if prior.evidence.outcome != "success":
                continue
            prior_entry = self.catalog.entry(prior.action.service)
            prior_group = prior_entry.equivalence_group or prior_entry.service
            if prior_group == group:
                return Decision.DENY, "equivalent service already succeeded"

        return Decision.PERMIT, "permitted"
