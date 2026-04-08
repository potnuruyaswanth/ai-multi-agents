from __future__ import annotations

import importlib

from agents.form_agent.tools import autofill_preview

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def preview_form_fill(form_url: str, context: str = "") -> dict:
    return autofill_preview(form_url, context)


root_agent = (
    Agent(name="form_agent", description="Provides auto-fill preview with manual final submit.", tools=[preview_form_fill])
    if Agent
    else None
)
