from __future__ import annotations

import re
from datetime import datetime, timedelta

from integrations.gmail_service import list_inbox_messages


def classify_email(subject: str, body: str) -> str:
    text = f"{subject} {body}".lower()
    if any(token in text for token in ["interview", "apply", "application", "job", "internship"]):
        return "job"
    if any(token in text for token in ["hackathon", "tech event", "register now", "event"]):
        return "hackathon"
    if any(token in text for token in ["meeting", "cabin", "faculty", "appointment"]):
        return "meeting"
    if any(token in text for token in ["deadline", "assessment", "submission"]):
        return "event"
    return "other"


def extract_datetime(body: str) -> datetime | None:
    body_lower = body.lower()
    now = datetime.utcnow()
    if "tomorrow" in body_lower:
        return now + timedelta(days=1)
    if "today" in body_lower:
        return now

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?", body)
    if date_match:
        date_part = date_match.group(1)
        time_part = date_match.group(2) or "09:00"
        return datetime.fromisoformat(f"{date_part} {time_part}")
    return None


def extract_action_link(body: str) -> str | None:
    url_match = re.search(r"https?://\S+", body)
    return url_match.group(0) if url_match else None


def fetch_recent_gmail_messages(user_id: str = "default-user", query: str = "newer_than:7d", max_results: int = 10) -> list[dict]:
    return list_inbox_messages(user_id=user_id, query=query, max_results=max_results)
