#!/usr/bin/env python3
"""Optionally confirm successful transaction receipts referenced by an artifact bundle.

This mirrors the paper's settlement-receipt verification scope. It checks transaction
existence and status only; it intentionally does not decode transfer logs to prove
asset, recipient, or atomic amount.
"""
from pathlib import Path
import argparse, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifiable_task_lifecycles.verifier import verify_external_run

p=argparse.ArgumentParser()
p.add_argument('--rpc-url', required=True)
p.add_argument('--run', default=str(ROOT/'experiments/external_interop/run.json'))
a=p.parse_args()
from web3 import Web3
run=json.loads(Path(a.run).read_text())
report=verify_external_run(run)
if not report.verified:
    print(report.issues); raise SystemExit(1)
w3=Web3(Web3.HTTPProvider(a.rpc_url))
for tx in report.settlement_refs:
    receipt=w3.eth.get_transaction_receipt(tx)
    ok=receipt is not None and int(receipt.status)==1
    print(tx, 'success' if ok else 'failed')
    if not ok: raise SystemExit(1)
