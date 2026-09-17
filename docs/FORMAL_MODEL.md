# Formal Model

The paper defines:

- `I = (g, C)` — Intent
- `A_t = (op, provider, service, params, value)` — Action
- `P_t = (actionId, payer, payee, amount, settlementRef, protocol, network)` — Payment
- `E_t = (instanceId, actionId, result, outcome, receiptRef)` — Evidence
- `L = (iota, I, M, s, H)` — task context
- `admit_t` — state, authorization, budget, and history-aware admission
- `bound_t` — Action/Payment/Evidence binding
- `fresh_t` — settlement-reference freshness
- `R_t` — fixed-size DLT transition record

Implementation mapping:

- `model.py` — lifecycle objects and task state
- `policy.py` — admission checks
- `controller.py` — execution and recording
- `verifier.py` — post-run verification
- `canonical.py` — canonical JSON and SHA-256 identifiers

The Solidity contract enforces creator authorization, ordered state, terminal constraints, and fixed-size commitments. Semantic admission remains off-chain.
