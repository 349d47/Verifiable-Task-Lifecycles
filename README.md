# Verifiable Task Lifecycles for Autonomous Economic Agents Using Distributed Ledgers

Prototype and experiment material for the paper **“Verifiable Task Lifecycles for Autonomous Economic Agents Using Distributed Ledgers.”**

The prototype represents a delegated economic task as one persistent lifecycle. Each accepted transition links **Intent**, **Action**, **Payment**, and **Evidence**. Complete objects remain off-chain. Content commitments, task state, and transition order are recorded on a distributed ledger and can later be checked against the exported artifacts.

The prototype is implemented in Python 3.13 with the OpenAI Responses API, x402 v2, web3.py, and a Solidity `LifecycleTracker` contract. The paper uses Base Sepolia.

Public deployment:

- Network: Base Sepolia (`eip155:84532`)
- Lifecycle contract: `0xE27e67da9D39aF51D778648E50EE2182C5B2D680`
- Controller/payer: `0xF482471FE90aC83376554054c039F188CB6CFA87`
- Payment protocol: x402 v2 `exact`

No private key or model-provider credential is included.

## Installation and Usage

### 1. Project Setup

Python 3.13 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The deterministic tests use only the Python standard library.

### 2. Deterministic Checks

```bash
python -m unittest discover -s tests -v
```

The 12 tests cover the six paper cases and additional binding, freshness, and terminal-state checks.

### 3. Archived Experiment Results

```bash
python scripts/validate_results.py
python scripts/summarize_live_runs.py
python scripts/verify_external_artifacts.py
```

These commands use the archived experiment records. They reproduce the five controlled Base Sepolia runs, 8 paid transitions, 18 lifecycle transactions, and the external-provider artifact commitments.

### 4. Receipt Checks

With `web3` installed and an RPC endpoint:

```bash
python scripts/verify_settlement_receipts.py --rpc-url https://sepolia.base.org
```

This checks transaction existence and successful receipt status. Transfer logs are not decoded.

### 5. Live Experiments

Copy `.env.example` to `.env` and add local credentials. Start the controlled provider, for example:

```bash
uvicorn services.controlled_provider:app --port 4021
```

A new live run produces new testnet observations. It does not reproduce historical confirmation times.

## Project Structure

```text
verifiable-task-lifecycles
│
├── contracts/                  Solidity lifecycle contract and tests
├── docs/                       model, architecture, reproduction
├── experiments/
│   ├── controlled_cases/       deterministic lifecycle cases
│   ├── live_base_sepolia/      five controlled end-to-end runs
│   ├── independent_verification/
│   └── external_interop/       separate external-provider run
├── scripts/                    validation and reproduction scripts
├── services/                   deterministic controlled provider
├── src/verifiable_task_lifecycles/
└── tests/                      deterministic tests
```

## Evaluation Material

- **RQ1:** `experiments/controlled_cases/` and `tests/`
- **RQ2:** `experiments/independent_verification/`
- **RQ3:** `experiments/live_base_sepolia/`
- **Interoperability:** `experiments/external_interop/`

The external-provider run is separate from the five-run performance sample.

## Source Provenance

The archived experiment files are preserved as recorded. The Python and Solidity source in this repository are provided as a reference implementation aligned with the final paper and archived artifact schema.

## Citation

Anonymized
