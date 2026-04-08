from __future__ import annotations

from datetime import datetime
from typing import Any

from googleapiclient.discovery import build

from integrations.google_oauth import load_credentials


def _calendar_service(user_id: str = "default-user"):
    credentials = load_credentials("calendar", user_id)
    if not credentials:
        return None
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


def create_google_calendar_event(
    title: str,
    start_at: datetime,
    end_at: datetime | None = None,
    event_type: str = "event",
    location: str = "",
    description: str = "",
    user_id: str = "default-user",
) -> dict[str, Any] | None:
    service = _calendar_service(user_id)
    if service is None:
        return None

    payload = {
        "summary": title,
        "location": location,
        "description": description or f"Auto-created {event_type} event.",
        "start": {"dateTime": start_at.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": (end_at or start_at).isoformat(), "timeZone": "UTC"},
    }
    created = service.events().insert(calendarId="primary", body=payload).execute()
    return created


def list_google_calendar_events(start: datetime, end: datetime, user_id: str = "default-user", max_results: int = 20) -> list[dict[str, Any]]:
    service = _calendar_service(user_id)
    if service is None:
        return []

    response = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
            maxResults=max_results,
        )
        .execute()
    )
    return response.get("items", [])
