# LifecycleTracker

Reference Solidity contract for the ledger functions described in the paper:

- task creation with Intent, lifecycle-state-model, and policy commitments;
- creator/controller authorization;
- monotone transition order;
- fixed-size Action/Payment/Evidence commitments;
- current task state;
- separate terminal finalization.

Semantic policy evaluation remains off-chain.

The paper deployment is `0xE27e67da9D39aF51D778648E50EE2182C5B2D680` on Base Sepolia. The exact historical build metadata was not retained; see `docs/PROVENANCE.md`.

Run the tests with:

```bash
forge test
```
