from __future__ import annotations

from datetime import timezone
from uuid import uuid4
from datetime import datetime

from integrations.calendar_service import create_google_calendar_event, list_google_calendar_events
from database.models import Event
from database.repository import Repository, new_event


repo = Repository()


def create_calendar_event(
    title: str,
    start_at: datetime,
    end_at: datetime | None = None,
    event_type: str = "event",
    source_email_id: str | None = None,
    user_id: str = "default-user",
):
    event = new_event(
        title=title,
        start_at=start_at,
        end_at=end_at,
        event_type=event_type,
        source_email_id=source_email_id,
    )
    create_google_calendar_event(
        title=title,
        start_at=start_at,
        end_at=end_at,
        event_type=event_type,
        user_id=user_id,
    )
    return repo.create_event(event)


def list_events(start: datetime | None = None, end: datetime | None = None, user_id: str = "default-user"):
    local_events = repo.list_events(start=start, end=end)
    if start and end:
        remote_events = list_google_calendar_events(start=start, end=end, user_id=user_id)
        merged: list[Event] = list(local_events)
        for remote_event in remote_events:
            remote_start = remote_event.get("start", {}).get("dateTime") or remote_event.get("start", {}).get("date")
            remote_end = remote_event.get("end", {}).get("dateTime") or remote_event.get("end", {}).get("date")
            if not remote_start or not remote_end:
                continue
            merged.append(
                Event(
                    event_id=remote_event.get("id", str(uuid4())),
                    title=remote_event.get("summary", "Google Calendar Event"),
                    start_at=datetime.fromisoformat(remote_start.replace("Z", "+00:00")),
                    end_at=datetime.fromisoformat(remote_end.replace("Z", "+00:00")),
                    type="event",
                    location=remote_event.get("location", ""),
                    created_at=datetime.now(timezone.utc),
                )
            )
        return merged
    return local_events
