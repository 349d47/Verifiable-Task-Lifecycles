# Architecture

The architecture follows Fig. 1 of the paper and separates four zones:

1. **Agent Controller Environment** — LLM Client, Lifecycle Controller, Policy Evaluator, Payment Client, Artifact Manager.
2. **External Services** — LLM API and paid x402 services.
3. **Persistence Layer** — Lifecycle Contract and off-chain Artifact Store.
4. **Independent Verification** — off-chain verifier.

The planner selects an advertised service. Trusted application code resolves endpoint, price, wallet, and transaction parameters. A denied Action has no economic effect. For a permitted Action, the service is invoked, Action/Payment/Evidence are stored, bindings are checked, and their commitments are recorded under the task instance.
