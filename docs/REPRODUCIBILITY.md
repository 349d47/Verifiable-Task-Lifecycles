# Reproducibility

## Deterministic Checks

```bash
python -m unittest discover -s tests -v
```

Runs 12 lifecycle and integrity tests without network access or credentials.

## Archived Results

```bash
python scripts/validate_results.py
python scripts/summarize_live_runs.py
python scripts/verify_external_artifacts.py
```

These scripts operate on the archived experiment files used for the reported results.

## Receipt Checks

```bash
python scripts/verify_settlement_receipts.py --rpc-url https://sepolia.base.org
```

Requires `web3` and network access. The check is limited to transaction existence and successful receipt status.

## New Live Runs

1. Install `requirements.txt`.
2. Copy `.env.example` to `.env` and add local credentials.
3. Start the controlled provider, e.g. `uvicorn services.controlled_provider:app --port 4021`.
4. Run new tasks with the planner, x402 client, controller, and a compatible lifecycle contract.

New runs produce new observations and can spend test assets. Do not commit credentials.

