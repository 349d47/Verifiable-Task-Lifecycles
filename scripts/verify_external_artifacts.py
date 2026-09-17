#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifiable_task_lifecycles.verifier import verify_external_run

run=json.loads((ROOT/'experiments/external_interop/run.json').read_text())
report=verify_external_run(run)
print(json.dumps({
    'verified': report.verified,
    'issues': report.issues,
    'transition_count': report.transition_count,
    'intent_id': report.intent_id,
    'settlement_refs': report.settlement_refs,
}, indent=2))
raise SystemExit(0 if report.verified else 1)
