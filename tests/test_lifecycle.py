import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from verifiable_task_lifecycles.canonical import content_id
from verifiable_task_lifecycles.controller import LifecycleController, TaskContext
from verifiable_task_lifecycles.model import ActionProposal, Evidence, Intent, Payment, TaskState
from verifiable_task_lifecycles.policy import CatalogEntry, Decision, PolicyEvaluator, TrustedCatalog
from verifiable_task_lifecycles.verifier import verify_artifact_bundle


def setup_components():
    catalog = TrustedCatalog([
        CatalogEntry("history", "controlled", 1, "http://provider/history", "0xpay", "history"),
        CatalogEntry("reputation", "controlled", 2, "http://provider/reputation", "0xpay", "reputation"),
        CatalogEntry("reputation-alt", "controlled", 2, "http://provider/reputation-alt", "0xpay", "reputation"),
        CatalogEntry("graph", "controlled", 3, "http://provider/graph", "0xpay", "graph"),
        CatalogEntry("forensics", "controlled", 6, "http://provider/forensics", "0xpay", "forensics"),
    ])
    intent = Intent("assess risk", 10, tuple(catalog._by_service), ("controlled",))
    evaluator = PolicyEvaluator(catalog)
    controller = LifecycleController(evaluator)
    context = TaskContext("instance-1", intent)
    return catalog, evaluator, controller, context


def objects_for(context, action, ref="0xtx", outcome="success"):
    aid = content_id(action.as_artifact())
    payment = Payment(ref, "0xpayer", action.provider, action.value, aid, "x402-v2", "eip155:84532")
    evidence = Evidence(context.instance_id, aid, json.dumps({"service": action.service}), outcome, ref)
    return payment, evidence


class LifecycleTests(unittest.TestCase):
    # T1
    def test_01_valid_first_purchase_permitted(self):
        catalog, evaluator, _, context = setup_components()
        action = catalog.resolve(ActionProposal("reputation"))
        self.assertEqual(evaluator.evaluate(context.intent, context.state, context.history, action)[0], Decision.PERMIT)

    # T2
    def test_02_budget_overflow_denied(self):
        catalog, evaluator, controller, context = setup_components()
        action = catalog.resolve(ActionProposal("forensics")); p,e = objects_for(context, action, "0x1")
        controller.accept(context, action, p, e)
        second = catalog.resolve(ActionProposal("forensics"))
        self.assertEqual(evaluator.evaluate(context.intent, context.state, context.history, second)[0], Decision.DENY)

    # T3
    def test_03_equivalent_service_after_success_denied(self):
        catalog, evaluator, controller, context = setup_components()
        first = catalog.resolve(ActionProposal("reputation")); p,e = objects_for(context, first, "0x1")
        controller.accept(context, first, p, e)
        equivalent = catalog.resolve(ActionProposal("reputation-alt"))
        self.assertEqual(evaluator.evaluate(context.intent, context.state, context.history, equivalent)[0], Decision.DENY)

    # T4
    def test_04_fallback_after_insufficient_permitted(self):
        catalog, evaluator, controller, context = setup_components()
        first = catalog.resolve(ActionProposal("history")); p,e = objects_for(context, first, "0x1", "insufficient")
        controller.accept(context, first, p, e)
        fallback = catalog.resolve(ActionProposal("reputation"))
        self.assertEqual(evaluator.evaluate(context.intent, context.state, context.history, fallback)[0], Decision.PERMIT)

    # T5
    def test_05_purchase_after_completion_denied(self):
        catalog, evaluator, _, context = setup_components()
        LifecycleController.finalize(context, TaskState.COMPLETED)
        action = catalog.resolve(ActionProposal("reputation"))
        self.assertEqual(evaluator.evaluate(context.intent, context.state, context.history, action)[0], Decision.DENY)

    # T6
    def test_06_modified_evidence_detected(self):
        run = json.loads((ROOT / "experiments/external_interop/run.json").read_text())
        bundle = copy.deepcopy(run["artifacts"])
        eid = next(iter(bundle["evidence"]))
        bundle["evidence"][eid]["result"] += "tampered"
        self.assertFalse(verify_artifact_bundle(bundle, run["instance_id"]).verified)

    def test_07_payment_substitution_across_actions_detected(self):
        run = json.loads((ROOT / "experiments/external_interop/run.json").read_text())
        bundle = copy.deepcopy(run["artifacts"])
        pid = next(iter(bundle["payments"])); bundle["payments"][pid]["action_id"] = "00" * 32
        self.assertFalse(verify_artifact_bundle(bundle, run["instance_id"]).verified)

    def test_08_payment_modification_detected(self):
        run = json.loads((ROOT / "experiments/external_interop/run.json").read_text())
        bundle = copy.deepcopy(run["artifacts"])
        pid = next(iter(bundle["payments"])); bundle["payments"][pid]["amount"] += 1
        self.assertFalse(verify_artifact_bundle(bundle, run["instance_id"]).verified)

    def test_09_planner_cannot_set_economic_terms(self):
        catalog, *_ = setup_components()
        with self.assertRaises(ValueError):
            catalog.resolve({"service":"reputation", "parameters":{}, "value":0, "provider":"attacker"})

    def test_10_reused_settlement_reference_rejected(self):
        catalog, _, controller, context = setup_components()
        first = catalog.resolve(ActionProposal("history")); p,e = objects_for(context, first, "0xreused", "insufficient")
        controller.accept(context, first, p, e)
        second = catalog.resolve(ActionProposal("reputation")); p2,e2 = objects_for(context, second, "0xreused", "success")
        self.assertIn("settlement reference reused", controller.validate_binding(context, second, p2, e2))

    def test_11_evidence_from_other_instance_detected(self):
        catalog, _, controller, context = setup_components()
        action = catalog.resolve(ActionProposal("reputation")); p,e = objects_for(context, action, "0x1")
        bad = Evidence("another-instance", e.action_id, e.result, e.outcome, e.receipt_ref)
        self.assertIn("Evidence.instance_id mismatch", controller.validate_binding(context, action, p, bad))

    def test_12_terminal_finalization_is_irreversible(self):
        _, _, _, context = setup_components()
        LifecycleController.finalize(context, TaskState.COMPLETED)
        with self.assertRaises(ValueError):
            LifecycleController.finalize(context, TaskState.FAILED)


if __name__ == "__main__": unittest.main()
