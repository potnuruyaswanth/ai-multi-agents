from __future__ import annotations

import importlib

from agents.chatbot_agent.tools import answer_query

try:
    Agent = importlib.import_module("google.adk.agents").Agent
    tool = importlib.import_module("google.adk.tools").tool
except Exception:  # pragma: no cover
    Agent = None

    def tool(func):
        return func


@tool
def ask_assistant(message: str) -> str:
    return answer_query(message)


root_agent = (
    Agent(name="chatbot_agent", description="Answers natural language productivity questions.", tools=[ask_assistant])
    if Agent
    else None
)
