#!/usr/bin/env python3
from pathlib import Path
import json, math, statistics, sys
ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'experiments/live_base_sepolia/results'
paths=sorted(RESULTS.glob('live_run_*.json'))
runs=[json.loads(p.read_text()) for p in paths]
assert len(runs)==5, len(runs)
assert all(r['verified'] for r in runs)
transitions=sum(sum(1 for t in r['trace'] if t.get('planner_kind')=='action') for r in runs)
assert transitions==8, transitions
rows=[m for r in runs for m in r['ledger_metrics']]
assert len(rows)==18
assert sum(m['gas_used'] for m in rows)==1_890_170
assert sum(r['spent_units'] for r in runs)==13
assert sorted(r['spent_units'] for r in runs)==[2,2,3,3,3]

summary=json.loads((RESULTS/'live_summary.json').read_text())
assert summary['runs']==5 and summary['all_verified'] is True
by={x['operation']:x for x in summary['operations']}
expected={
 'create_instance':(5,115877.8,533.452,485.884),
 'record_transition':(8,145316.5,288.904,267.642),
 'finalize_instance':(5,29649.8,385.312,250.037),
}
for op,(n,g,l,med) in expected.items():
    s=by[op]
    assert s['n']==n
    assert math.isclose(s['gas_mean'],g,abs_tol=1e-9)
    assert math.isclose(s['latency_mean_ms'],l,abs_tol=1e-9)
    assert math.isclose(s['latency_median_ms'],med,abs_tol=1e-9)

mean_gas=sum(m['gas_used'] for m in rows)/5
mean_latency=sum(m['latency_ms'] for m in rows)/5/1000
fees=sum(m['gas_used']*m['effective_gas_price']/1e18 for m in rows)
assert math.isclose(mean_gas,378034,abs_tol=1e-9)
assert math.isclose(mean_latency,1.381011,abs_tol=1e-9)
assert math.isclose(fees,1.156e-5,rel_tol=5e-4)

external=json.loads((ROOT/'experiments/external_interop/final_verification.json').read_text())
assert external['verified'] is True and external['issues']==[]
assert external['transition_count']==1 and external['final_state']==2
assert external['settlement_receipts_verified']==1 and external['finalization_receipt_verified'] is True
assert external['verification_block']==46840327
ind=json.loads((ROOT/'experiments/independent_verification/result.json').read_text())
assert ind['verified'] is True and ind['issues']==[] and ind['transition_count']==2
assert ind['settlement_receipts_verified']==2
print('archived results: OK')
print('5 runs, 8 paid transitions, 18 lifecycle transactions')
print('total gas: 1,890,170; mean/task: 378,034')
print(f'mean summed confirmation time/task: {mean_latency:.7f} s')
print(f'total lifecycle fees from receipts: {fees:.12g} ETH')
