# Controlled Paid Services

`controlled_provider.py` implements the deterministic services used for controlled experiments.

| Service | Budget units | Outcome |
|---|---:|---|
| transaction history | 1 | `insufficient` |
| reputation | 2 | `success` |
| graph analysis | 3 | `success` |
| forensics | 6 | `success` |

One lifecycle budget unit corresponds to 0.01 USDC in the controlled setup. The provider can be wrapped with x402 v2 `exact` middleware on Base Sepolia.

New executions create new observations. Archived paper runs are under `experiments/live_base_sepolia/`.
