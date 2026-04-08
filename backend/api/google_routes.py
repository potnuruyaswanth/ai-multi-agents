from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from agents.notification_agent.tools import remind_upcoming_items
from agents.task_agent.tools import sync_local_tasks_to_google
from integrations.calendar_service import create_google_calendar_event, list_google_calendar_events
from integrations.drive_service import application_asset_links, list_google_drive_files
from integrations.gmail_service import list_inbox_messages
from integrations.google_oauth import connection_status
from integrations.tasks_service import list_google_task_lists, list_google_tasks

router = APIRouter(prefix="/google", tags=["google-integrations"])


@router.get("/gmail/messages")
def get_gmail_messages(user_id: str = Query(default="default-user"), query: str = Query(default="newer_than:7d")):
    return {"messages": list_inbox_messages(user_id=user_id, query=query)}


@router.get("/status")
def get_google_status(user_id: str = Query(default="default-user")):
    return {
        "gmail": connection_status("gmail", user_id),
        "calendar": connection_status("calendar", user_id),
        "tasks": connection_status("tasks", user_id),
        "drive": connection_status("drive", user_id),
    }


@router.post("/gmail/sync")
def sync_gmail_messages(user_id: str = Query(default="default-user"), query: str = Query(default="newer_than:7d")):
    messages = list_inbox_messages(user_id=user_id, query=query)
    processed = []

    from agents.orchestrator_agent.tools import process_email_workflow

    for message in messages:
        body = message.get("snippet") or message.get("body_hint") or ""
        result = process_email_workflow(
            email_id=message.get("email_id", ""),
            subject=message.get("subject", ""),
            sender=message.get("sender", ""),
            body=body,
        )
        processed.append({"email_id": message.get("email_id"), "category": result["category"]})

    return {"count": len(processed), "processed": processed}


@router.post("/calendar/event")
def create_google_event(
    title: str,
    start_iso: str,
    end_iso: str | None = None,
    event_type: str = "event",
    user_id: str = Query(default="default-user"),
):
    start_at = datetime.fromisoformat(start_iso)
    end_at = datetime.fromisoformat(end_iso) if end_iso else None
    event = create_google_calendar_event(title, start_at, end_at, event_type=event_type, user_id=user_id)
    return {"event": event}


@router.get("/calendar/events")
def get_google_events(
    start_iso: str | None = None,
    end_iso: str | None = None,
    user_id: str = Query(default="default-user"),
):
    start = datetime.fromisoformat(start_iso) if start_iso else datetime.utcnow() - timedelta(days=7)
    end = datetime.fromisoformat(end_iso) if end_iso else datetime.utcnow() + timedelta(days=30)
    events = list_google_calendar_events(start=start, end=end, user_id=user_id)
    return {"events": events}


@router.get("/tasks/lists")
def get_google_task_lists(user_id: str = Query(default="default-user")):
    return {"task_lists": list_google_task_lists(user_id=user_id)}


@router.get("/tasks/items")
def get_google_tasks(
    user_id: str = Query(default="default-user"),
    tasklist_id: str | None = None,
):
    return {"tasks": list_google_tasks(user_id=user_id, tasklist_id=tasklist_id)}


@router.post("/tasks/sync")
def sync_tasks(user_id: str = Query(default="default-user")):
    return sync_local_tasks_to_google(user_id=user_id)


@router.get("/drive/files")
def get_drive_files(user_id: str = Query(default="default-user"), max_results: int = Query(default=25)):
    return {"files": list_google_drive_files(user_id=user_id, max_results=max_results)}


@router.get("/drive/resources")
def get_drive_resources(user_id: str = Query(default="default-user")):
    return {"resources": application_asset_links(user_id=user_id)}


@router.post("/reminders/run")
def run_reminders(user_email: str = Query(default="student@example.com"), hours_ahead: int = Query(default=24)):
    reminders = remind_upcoming_items(user_email=user_email, hours_ahead=hours_ahead)
    return {"count": len(reminders), "reminders": reminders}
