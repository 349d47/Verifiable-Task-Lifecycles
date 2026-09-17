# Controlled Base Sepolia Runs (RQ3)

Five archived end-to-end runs used for the controlled performance sample:

- 5 `createInstance` transactions
- 8 `recordTransition` transactions
- 5 `finalizeInstance` transactions
- 18 lifecycle transactions total
- two runtime-selected paths

`results/live_summary.json` and `.csv` contain the reported operation-level summaries. Recompute them with:

```bash
python scripts/summarize_live_runs.py
```

The sample characterizes the recorded workflow and is not a Base Sepolia network benchmark.
