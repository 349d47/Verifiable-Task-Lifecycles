from __future__ import annotations

import os
from fastapi import FastAPI

RESPONSES = {
    "history": {"outcome": "insufficient", "activity": True, "reason": "history alone is inconclusive"},
    "reputation": {"outcome": "success", "elevated_risk": True, "confidence": 0.78},
    "graph": {"outcome": "success", "elevated_risk": True, "confidence": 0.81},
    "forensics": {"outcome": "success", "elevated_risk": True, "confidence": 0.88},
}
PRICES = {"history": "$0.01", "reputation": "$0.02", "graph": "$0.03", "forensics": "$0.06"}


def create_app(with_x402: bool = True) -> FastAPI:
    app = FastAPI(title="Controlled deterministic lifecycle services")

    @app.post("/history")
    async def history(payload: dict): return {"service": "history", **RESPONSES["history"], "input": payload}

    @app.post("/reputation")
    async def reputation(payload: dict): return {"service": "reputation", **RESPONSES["reputation"], "input": payload}

    @app.post("/graph")
    async def graph(payload: dict): return {"service": "graph", **RESPONSES["graph"], "input": payload}

    @app.post("/forensics")
    async def forensics(payload: dict): return {"service": "forensics", **RESPONSES["forensics"], "input": payload}

    if with_x402:
        from x402.http import FacilitatorConfig, HTTPFacilitatorClient, PaymentOption
        from x402.http.middleware.fastapi import PaymentMiddlewareASGI
        from x402.http.types import RouteConfig
        from x402.mechanisms.evm.exact import ExactEvmServerScheme
        from x402.server import x402ResourceServer

        pay_to = os.environ["PAY_TO_ADDRESS"]
        facilitator_url = os.getenv("X402_FACILITATOR_URL", "https://x402.org/facilitator")
        facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=facilitator_url))
        server = x402ResourceServer(facilitator)
        server.register("eip155:84532", ExactEvmServerScheme())
        routes = {
            f"POST /{service}": RouteConfig(accepts=[PaymentOption(
                scheme="exact", pay_to=pay_to, price=price, network="eip155:84532"
            )], description=f"Deterministic {service} analysis", mime_type="application/json")
            for service, price in PRICES.items()
        }
        app.add_middleware(PaymentMiddlewareASGI, routes=routes, server=server)

    return app


app = create_app(with_x402=os.getenv("DISABLE_X402", "0") != "1")
