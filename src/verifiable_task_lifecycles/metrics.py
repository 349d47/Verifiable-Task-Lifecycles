from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, median
from typing import Iterable, Any


@dataclass(frozen=True)
class OperationSummary:
    operation: str
    n: int
    gas_mean: float
    gas_min: int
    gas_max: int
    latency_mean_ms: float
    latency_median_ms: float
    latency_min_ms: float
    latency_max_ms: float
    fee_mean_eth: float


def summarize_runs(runs: Iterable[dict[str, Any]]) -> list[OperationSummary]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        for row in run.get("ledger_metrics", []):
            grouped[row["operation"]].append(row)

    summaries: list[OperationSummary] = []
    for operation in sorted(grouped):
        rows = grouped[operation]
        gas = [int(r["gas_used"]) for r in rows]
        latency = [float(r["latency_ms"]) for r in rows]
        fees = [int(r["gas_used"]) * int(r["effective_gas_price"]) / 1e18 for r in rows]
        summaries.append(OperationSummary(
            operation=operation,
            n=len(rows),
            gas_mean=mean(gas), gas_min=min(gas), gas_max=max(gas),
            latency_mean_ms=mean(latency), latency_median_ms=median(latency),
            latency_min_ms=min(latency), latency_max_ms=max(latency),
            fee_mean_eth=mean(fees),
        ))
    return summaries
