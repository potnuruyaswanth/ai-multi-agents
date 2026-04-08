from __future__ import annotations

from datetime import datetime, timedelta

from agents.calendar_agent.tools import list_events
from agents.task_agent.tools import list_tasks


def parse_time_window(message: str) -> tuple[datetime, datetime]:
    now = datetime.utcnow()
    text = message.lower()
    if "tomorrow" in text:
        start = datetime(now.year, now.month, now.day) + timedelta(days=1)
        end = start + timedelta(days=1)
        return start, end
    if "week" in text:
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=7)
        return start, end
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    return start, end


def answer_query(message: str) -> str:
    text = message.lower()
    start, end = parse_time_window(text)

    if any(word in text for word in ["task", "todo", "checklist", "deadline"]):
        tasks = list_tasks(start=start, end=end)
        if not tasks:
            return "No tasks found for that period."
        summary = "\n".join([f"- {t.title} ({t.priority})" for t in tasks[:5]])
        return f"You have {len(tasks)} tasks:\n{summary}"

    if any(word in text for word in ["event", "meeting", "calendar", "hackathon"]):
        events = list_events(start=start, end=end)
        if not events:
            return "No events found for that period."
        summary = "\n".join([f"- {e.title} at {e.start_at.isoformat()}" for e in events[:5]])
        return f"You have {len(events)} events:\n{summary}"

    tasks = list_tasks(start=start, end=end)
    events = list_events(start=start, end=end)
    return f"Summary: {len(tasks)} tasks and {len(events)} events in the selected window."
