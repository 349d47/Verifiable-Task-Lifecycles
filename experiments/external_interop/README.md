# External-Provider Interoperability

Separate Base Sepolia run with an independently operated x402 sanctions-screening service. It is not part of the five-run controlled performance sample.

- `run.json` — Action, Payment, Evidence, artifact bundle, settlement reference, and service response
- `final_verification.json` — final verifier result (`verified: true`)
- `diagnostics/verification_before_finalization.json` — intermediate check before finalization

Recompute the archived content identifiers and bindings with:

```bash
python scripts/verify_external_artifacts.py
```
