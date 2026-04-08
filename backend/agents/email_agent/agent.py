from __future__ import annotations

import importlib

from agents.email_agent.tools import classify_email, extract_action_link, extract_datetime, fetch_recent_gmail_messages

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def read_and_classify_email(subject: str, body: str) -> dict:
    return {
        "category": classify_email(subject, body),
        "detected_datetime": extract_datetime(body).isoformat() if extract_datetime(body) else None,
        "action_link": extract_action_link(body),
    }


@tool
def read_recent_gmail_messages(user_id: str = "default-user", query: str = "newer_than:7d", max_results: int = 10) -> list[dict]:
    return fetch_recent_gmail_messages(user_id=user_id, query=query, max_results=max_results)


root_agent = (
    Agent(
        name="email_agent",
        description="Reads and classifies Gmail messages.",
        tools=[read_and_classify_email, read_recent_gmail_messages],
    )
    if Agent
    else None
)
