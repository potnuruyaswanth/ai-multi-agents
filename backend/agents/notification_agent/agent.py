from __future__ import annotations

import importlib

from agents.notification_agent.tools import send_notification_email

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def send_notification(to_email: str, subject: str, message: str) -> dict:
    return send_notification_email(to_email, subject, message).model_dump()


root_agent = (
    Agent(name="notification_agent", description="Sends and logs notifications.", tools=[send_notification]) if Agent else None
)
