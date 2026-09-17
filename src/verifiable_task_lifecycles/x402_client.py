from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PaidResponse:
    body: Any
    transaction: str
    network: str
    payer: str | None
    settlement: dict[str, Any]


def _decode_header(value: str) -> dict[str, Any]:
    value += "=" * (-len(value) % 4)
    return json.loads(base64.b64decode(value).decode("utf-8"))


class X402PaymentClient:
    """x402 v2 `exact` HTTP client adapter used by live experiments.

    Imports match the x402 Python v2 API used by the archived environment. The
    default test suite never instantiates this class and therefore never spends funds.
    """

    def __init__(self, private_key: str):
        from eth_account import Account
        from x402 import x402Client
        from x402.mechanisms.evm import EthAccountSigner
        from x402.mechanisms.evm.exact.register import register_exact_evm_client

        account = Account.from_key(private_key)
        client = x402Client()
        register_exact_evm_client(client, EthAccountSigner(account))
        self._client = client

    async def request(self, method: str, url: str, *, json_body: Any | None = None) -> PaidResponse:
        from x402.http.clients import x402HttpxClient

        async with x402HttpxClient(self._client) as http:
            response = await http.request(method=method, url=url, json=json_body)
            await response.aread()
            response.raise_for_status()
            header = response.headers.get("PAYMENT-RESPONSE")
            if not header:
                raise RuntimeError("paid response did not contain PAYMENT-RESPONSE")
            settlement = _decode_header(header)
            if not settlement.get("success"):
                raise RuntimeError(f"x402 settlement failed: {settlement}")
            try:
                body = response.json()
            except Exception:
                body = response.text
            return PaidResponse(
                body=body,
                transaction=settlement["transaction"],
                network=settlement["network"],
                payer=settlement.get("payer"),
                settlement=settlement,
            )
