from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import ActionProposal


@dataclass(frozen=True)
class PlannerResult:
    kind: str
    proposal: ActionProposal | None = None
    reason: str | None = None
    summary: str | None = None
    response_id: str | None = None
    model: str | None = None


class OpenAIPlanner:
    """Small Responses API adapter using strict function calls.

    Live use requires the optional dependencies and OPENAI_API_KEY. The planner can
    select a service and parameters, but the trusted catalog resolves endpoint,
    price, provider wallet, protocol details, and blockchain calls.
    """

    def __init__(self, model: str = "gpt-5.6"):
        from openai import OpenAI
        self.client = OpenAI()
        self.model = model

    def choose(self, task_context: str, services: list[str]) -> PlannerResult:
        tools = [{
            "type": "function",
            "name": "select_service",
            "description": "Select one advertised paid service, or finish when enough evidence exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string", "enum": ["action", "finish"]},
                    "service": {"type": ["string", "null"], "enum": services + [None]},
                    "parameters": {"type": "object", "additionalProperties": True},
                    "reason": {"type": "string"},
                    "summary": {"type": ["string", "null"]},
                },
                "required": ["decision", "service", "parameters", "reason", "summary"],
                "additionalProperties": False,
            },
            "strict": True,
        }]
        response = self.client.responses.create(
            model=self.model,
            input=task_context,
            tools=tools,
            tool_choice={"type": "function", "name": "select_service"},
        )
        call = next(item for item in response.output if getattr(item, "type", None) == "function_call")
        import json
        args = json.loads(call.arguments)
        if args["decision"] == "finish":
            return PlannerResult(
                kind="finish", reason=args["reason"], summary=args["summary"],
                response_id=response.id, model=getattr(response, "model", self.model),
            )
        return PlannerResult(
            kind="action",
            proposal=ActionProposal(args["service"], args.get("parameters", {})),
            reason=args["reason"], response_id=response.id,
            model=getattr(response, "model", self.model),
        )
