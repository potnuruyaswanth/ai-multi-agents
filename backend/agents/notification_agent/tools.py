from __future__ import annotations

import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from config.settings import get_settings
from agents.task_agent.tools import list_tasks
from agents.calendar_agent.tools import list_events
from database.repository import Repository, new_notification


repo = Repository()


def collect_upcoming_items(hours_ahead: int = 24, user_id: str = "default-user") -> list[dict]:
    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=hours_ahead)
    items: list[dict] = []

    for task in list_tasks(start=now, end=window_end, user_id=user_id):
        items.append(
            {
                "type": "task",
                "title": task.title,
                "due_at": task.due_at.isoformat() if task.due_at else None,
                "priority": task.priority,
            }
        )

    for event in list_events(start=now, end=window_end, user_id=user_id):
        items.append(
            {
                "type": "event",
                "title": event.title,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat(),
                "event_type": event.type,
            }
        )

    return items


def send_notification_email(to_email: str, subject: str, message: str):
    notification = new_notification(to_email=to_email, subject=subject, message=message)
    settings = get_settings()

    if settings.smtp_user and settings.smtp_password:
        email_message = EmailMessage()
        email_message["Subject"] = subject
        email_message["From"] = settings.notification_sender_email or settings.smtp_user
        email_message["To"] = to_email
        email_message.set_content(message)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(email_message)

    return repo.create_notification(notification)


def remind_upcoming_items(user_email: str, hours_ahead: int = 24) -> list[dict]:
    items = collect_upcoming_items(hours_ahead=hours_ahead)
    reminders: list[dict] = []

    for item in items:
        subject = f"Reminder: {item['title']}"
        if item["type"] == "task":
            message = f"Task due at {item.get('due_at') or 'N/A'}"
        else:
            message = f"Event starts at {item.get('start_at')}"
        notification = send_notification_email(user_email, subject, message)
        reminders.append(notification.model_dump())

    return reminders


def build_daily_digest(user_email: str, user_id: str = "default-user", target_date: datetime | None = None) -> dict:
    current = target_date or datetime.now(timezone.utc)
    day_start = datetime(current.year, current.month, current.day, tzinfo=current.tzinfo or timezone.utc)
    day_end = day_start + timedelta(days=1)

    tasks = list_tasks(start=day_start, end=day_end)
    events = list_events(start=day_start, end=day_end, user_id=user_id)

    digest = {
        "date": day_start.date().isoformat(),
        "tasks_count": len(tasks),
        "events_count": len(events),
        "tasks": [
            {
                "title": task.title,
                "due_at": task.due_at.isoformat() if task.due_at else None,
                "priority": task.priority,
            }
            for task in tasks[:10]
        ],
        "events": [
            {
                "title": event.title,
                "start_at": event.start_at.isoformat(),
                "end_at": event.end_at.isoformat(),
                "type": event.type,
            }
            for event in events[:10]
        ],
        "summary": f"You have {len(tasks)} task(s) and {len(events)} event(s) today.",
    }

    digest["reminders"] = collect_upcoming_items(hours_ahead=24, user_id=user_id)
    digest["reminders_count"] = len(digest["reminders"])
    return digest
