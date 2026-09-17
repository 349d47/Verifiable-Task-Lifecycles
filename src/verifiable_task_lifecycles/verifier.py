from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .canonical import content_id


@dataclass
class VerificationReport:
    verified: bool
    issues: list[str] = field(default_factory=list)
    transition_count: int = 0
    intent_id: str | None = None
    settlement_refs: list[str] = field(default_factory=list)


def _state_name(value: Any) -> str:
    return str(value).strip().lower()


def verify_artifact_bundle(bundle: dict[str, Any], instance_id: str | None = None) -> VerificationReport:
    issues: list[str] = []
    intent = bundle.get("intent")
    actions: dict[str, Any] = bundle.get("actions", {})
    payments: dict[str, Any] = bundle.get("payments", {})
    evidence: dict[str, Any] = bundle.get("evidence", {})
    records: list[dict[str, Any]] = bundle.get("records", [])
    settlement_refs: list[str] = []

    if not isinstance(intent, dict):
        issues.append("missing Intent artifact")
        intent_id = None
    else:
        intent_id = content_id(intent)

    for identifier, obj in actions.items():
        if content_id(obj) != identifier:
            issues.append(f"Action content identifier mismatch: {identifier}")
    for identifier, obj in payments.items():
        if content_id(obj) != identifier:
            issues.append(f"Payment content identifier mismatch: {identifier}")
    for identifier, obj in evidence.items():
        if content_id(obj) != identifier:
            issues.append(f"Evidence content identifier mismatch: {identifier}")

    previous_next: str | None = None
    seen_settlements: set[str] = set()
    for expected_index, record in enumerate(records):
        if record.get("transition_no") != expected_index:
            issues.append(f"non-monotone transition index at position {expected_index}")
        if instance_id is not None and record.get("instance_id") != instance_id:
            issues.append(f"record {expected_index} has wrong instance_id")
        if previous_next is not None and _state_name(record.get("previous_state")) != previous_next:
            issues.append(f"state-chain mismatch at transition {expected_index}")

        aid = record.get("action_id")
        pid = record.get("payment_id")
        eid = record.get("evidence_id")
        action = actions.get(aid)
        payment = payments.get(pid)
        ev = evidence.get(eid)
        if action is None:
            issues.append(f"missing Action for transition {expected_index}")
            continue
        if payment is None:
            issues.append(f"missing Payment for transition {expected_index}")
            continue
        if ev is None:
            issues.append(f"missing Evidence for transition {expected_index}")
            continue

        # bound_t
        if payment.get("action_id") != aid:
            issues.append(f"Payment.action_id mismatch at transition {expected_index}")
        if ev.get("action_id") != aid:
            issues.append(f"Evidence.action_id mismatch at transition {expected_index}")
        if instance_id is not None and ev.get("instance_id") != instance_id:
            issues.append(f"Evidence.instance_id mismatch at transition {expected_index}")
        if payment.get("payee") != action.get("provider"):
            issues.append(f"Payment.payee mismatch at transition {expected_index}")
        if payment.get("amount") != action.get("value"):
            issues.append(f"Payment.amount mismatch at transition {expected_index}")
        receipt = ev.get("receipt_ref")
        settlement = payment.get("reference")
        if receipt is not None and receipt != settlement:
            issues.append(f"Evidence.receipt_ref mismatch at transition {expected_index}")

        # fresh_t
        if settlement:
            if settlement in seen_settlements:
                issues.append(f"reused settlement reference at transition {expected_index}")
            seen_settlements.add(settlement)
            settlement_refs.append(settlement)

        previous_next = _state_name(record.get("next_state"))

    return VerificationReport(
        verified=not issues,
        issues=issues,
        transition_count=len(records),
        intent_id=intent_id,
        settlement_refs=settlement_refs,
    )


def verify_external_run(run: dict[str, Any]) -> VerificationReport:
    instance_id = run.get("instance_id")
    bundle = run.get("artifacts")
    if not isinstance(bundle, dict):
        return VerificationReport(False, ["run does not contain an artifact bundle"])
    report = verify_artifact_bundle(bundle, instance_id=instance_id)

    if run.get("action_id") and content_id(run.get("action")) != run.get("action_id"):
        report.issues.append("top-level Action identifier mismatch")
    transition = run.get("transition") or {}
    if transition.get("payment_id") and content_id(run.get("payment")) != transition.get("payment_id"):
        report.issues.append("top-level Payment identifier mismatch")
    if run.get("evidence_id") and content_id(run.get("evidence")) != run.get("evidence_id"):
        report.issues.append("top-level Evidence identifier mismatch")
    report.verified = not report.issues
    return report
