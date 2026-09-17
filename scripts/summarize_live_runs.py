#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifiable_task_lifecycles.metrics import summarize_runs

paths=sorted((ROOT/'experiments/live_base_sepolia/results').glob('live_run_*.json'))
runs=[json.loads(p.read_text()) for p in paths]
print(f"runs: {len(runs)}")
print(f"paid transitions: {sum(sum(1 for x in r.get('trace',[]) if x.get('planner_kind')=='action') for r in runs)}")
for row in summarize_runs(runs):
    print(f"{row.operation:18s} n={row.n} gas_mean={row.gas_mean:.1f} gas_range={row.gas_min}-{row.gas_max} "
          f"latency_mean_ms={row.latency_mean_ms:.3f} median_ms={row.latency_median_ms:.3f} fee_mean_eth={row.fee_mean_eth:.12g}")
total_gas=sum(m['gas_used'] for r in runs for m in r['ledger_metrics'])
total_latency=sum(m['latency_ms'] for r in runs for m in r['ledger_metrics'])
print(f"total lifecycle gas: {total_gas}")
print(f"mean lifecycle gas/task: {total_gas/len(runs):.0f}")
print(f"mean summed confirmation time/task: {total_latency/len(runs)/1000:.6f} s")
