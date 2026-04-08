from __future__ import annotations

from datetime import datetime
import importlib
from agents.task_agent.tools import create_checklist_task, list_tasks

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def create_task(title: str, deadline_iso: str | None, source_email_id: str | None, checklist: list[str]):
    due_at = datetime.fromisoformat(deadline_iso) if deadline_iso else None
    return create_checklist_task(title, due_at, source_email_id, checklist).model_dump()


@tool
def get_tasks() -> list[dict]:
    return [task.model_dump() for task in list_tasks()]


root_agent = (
    Agent(name="task_agent", description="Creates and fetches task checklist items.", tools=[create_task, get_tasks])
    if Agent
    else None
)
