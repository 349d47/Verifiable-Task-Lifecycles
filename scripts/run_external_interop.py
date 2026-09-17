#!/usr/bin/env python3
"""Minimal live x402 interoperability call.

This is intentionally separate from the five controlled performance runs. It makes a
real paid request and therefore requires an explicit private key and test assets.
It does not write a lifecycle transition to the DLT; the full archived run is retained
in experiments/external_interop/run.json.
"""
import argparse, asyncio, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifiable_task_lifecycles.x402_client import X402PaymentClient

async def main():
    p=argparse.ArgumentParser()
    p.add_argument('--endpoint', required=True)
    p.add_argument('--name', default='Banco Nacional de Cuba')
    a=p.parse_args()
    key=os.environ.get('EVM_PRIVATE_KEY')
    if not key: raise SystemExit('EVM_PRIVATE_KEY is required for a live paid call')
    client=X402PaymentClient(key)
    response=await client.request('POST', a.endpoint, json_body={'name':a.name})
    print(json.dumps({'transaction':response.transaction,'network':response.network,'body':response.body}, indent=2))

if __name__=='__main__': asyncio.run(main())
