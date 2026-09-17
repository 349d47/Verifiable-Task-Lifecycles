# Claim-to-artifact map

| Paper claim/evaluation item | Repository evidence |
|---|---|
| T1-T5 lifecycle admission (RQ1) | `experiments/controlled_cases/cases.json`, `tests/test_lifecycle.py` tests 01-05 |
| T6 Evidence tamper detection | `tests/test_lifecycle.py` test 06, exact external artifact bundle in `experiments/external_interop/run.json` |
| Additional Payment substitution/modification checks | tests 07-08 |
| Planner cannot set economic terms directly | test 09 and `TrustedCatalog.resolve` |
| Settlement-reference freshness | test 10 |
| Cross-instance Evidence substitution | test 11 |
| Terminal lifecycle behavior | test 12 + Solidity tests |
| Five controlled Base Sepolia runs | `experiments/live_base_sepolia/results/live_run_*.json` |
| 8 paid transitions / two runtime paths | same raw run files; recomputed by `scripts/summarize_live_runs.py` |
| RQ3 gas/latency/fees | `live_summary.json`, `live_summary.csv`, raw receipt metrics, `scripts/validate_results.py` |
| Fresh two-transition independent verification (RQ2) | `experiments/independent_verification/result.json` |
| External-provider interoperability | `experiments/external_interop/run.json`, `final_verification.json` |
| Canonical JSON + SHA-256 commitments | `src/verifiable_task_lifecycles/canonical.py`; exact IDs recomputed from external run |
| Trust/scope limitations | `docs/TRUST_MODEL.md` and paper Section III-D/VI |
