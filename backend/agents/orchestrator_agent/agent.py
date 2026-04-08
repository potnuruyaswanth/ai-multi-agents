from __future__ import annotations

import importlib

from agents.orchestrator_agent.tools import chat_workflow, process_email_workflow, sync_gmail_inbox_workflow

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def process_email(email_id: str, subject: str, sender: str, body: str) -> dict:
    return dict(process_email_workflow(email_id, subject, sender, body))


@tool
def chat(message: str) -> str:
    return chat_workflow(message)


@tool
def sync_gmail(user_id: str = "default-user", query: str = "newer_than:7d") -> list[dict]:
    return [result for result in sync_gmail_inbox_workflow(user_id=user_id, query=query)]


root_agent = (
    Agent(
        name="orchestrator_agent",
        description="Primary coordinator agent for all automation workflows.",
        tools=[process_email, chat, sync_gmail],
    )
    if Agent
    else None
)
