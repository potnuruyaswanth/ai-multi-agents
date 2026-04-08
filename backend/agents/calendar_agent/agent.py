from __future__ import annotations

from datetime import datetime
import importlib
from agents.calendar_agent.tools import create_calendar_event, list_events

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def add_event(title: str, start_iso: str, end_iso: str | None, event_type: str, source_email_id: str | None):
    start_at = datetime.fromisoformat(start_iso)
    end_at = datetime.fromisoformat(end_iso) if end_iso else None
    return create_calendar_event(title, start_at, end_at, event_type, source_email_id).model_dump()


@tool
def get_events() -> list[dict]:
    return [event.model_dump() for event in list_events()]


root_agent = (
    Agent(name="calendar_agent", description="Handles schedule/event creation and retrieval.", tools=[add_event, get_events])
    if Agent
    else None
)
