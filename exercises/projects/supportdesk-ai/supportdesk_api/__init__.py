"""SupportDesk AI — help-desk assistant API.

The acceptance tests call:

    create_app({"jwt_secret": "...", "min_score": 0.15, "top_k": 4, "max_tool_steps": 4})  ->  a FastAPI app

Overrides beat the environment (JWT_SECRET). Defaults when a key is missing: min_score 0.15, top_k 4, max_tool_steps 4.

The tests replace these four dependencies (FastAPI dependency_overrides) — create them in supportdesk_api/deps.py:

    get_llm()         object with  .complete(system: str, messages: list[dict], tools: list[dict]) -> dict
    get_embedder()    object with  .embed(texts: list[str]) -> list[list[float]]
    get_orders_api()  object with  .get_order(order_id: str) -> dict | None
    get_tracer()      object with  .span(name, **attrs) -> context manager yielding an object with .set(**attrs)

and they import these names, so create the modules:

    supportdesk_api/guardrails.py   redact_pii(text) -> str,  injection_signals(text) -> list[str]
"""

from fastapi import FastAPI


def create_app(overrides: dict | None = None) -> FastAPI:
    raise NotImplementedError("Build the app factory — start with checkpoint C1 in README.md")
