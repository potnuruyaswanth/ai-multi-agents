from __future__ import annotations

from datetime import datetime, timedelta

from agents.calendar_agent.tools import create_calendar_event
from agents.chatbot_agent.tools import answer_query
from agents.email_agent.tools import classify_email, extract_action_link, extract_datetime, fetch_recent_gmail_messages
from agents.form_agent.tools import autofill_preview
from agents.notification_agent.tools import send_notification_email
from agents.task_agent.tools import create_checklist_task
from database.models import EmailRecord
from database.repository import Repository

repo = Repository()


class OrchestrationResult(dict):
    pass


def process_email_workflow(email_id: str, subject: str, sender: str, body: str) -> OrchestrationResult:
    category = classify_email(subject=subject, body=body)
    extracted_time = extract_datetime(body)
    action_link = extract_action_link(body)

    email_record = EmailRecord(
        email_id=email_id,
        subject=subject,
        sender=sender,
        body=body,
        category=category,
        processed_status="processed",
        metadata={"action_link": action_link},
    )
    repo.save_email(email_record)

    tasks_created = 0
    events_created = 0
    notifications_sent = 0

    if category == "job":
        checklist = ["Review JD", "Update resume", "Apply via link"]
        create_checklist_task(
            title=f"Apply: {subject}",
            due_at=extracted_time or (datetime.utcnow() + timedelta(days=1)),
            source_email_id=email_id,
            checklist=checklist,
            priority="high",
        )
        tasks_created += 1

        create_calendar_event(
            title=f"Deadline: {subject}",
            start_at=extracted_time or (datetime.utcnow() + timedelta(days=1)),
            event_type="deadline",
            source_email_id=email_id,
        )
        events_created += 1

    elif category == "hackathon":
        create_calendar_event(
            title=f"Hackathon: {subject}",
            start_at=extracted_time or (datetime.utcnow() + timedelta(days=2)),
            event_type="hackathon",
            source_email_id=email_id,
        )
        events_created += 1

        create_checklist_task(
            title=f"Register: {subject}",
            due_at=extracted_time,
            source_email_id=email_id,
            checklist=["Open registration", "Fill details", "Confirm registration"],
            priority="medium",
        )
        tasks_created += 1

    elif category == "meeting":
        start_time = extracted_time or (datetime.utcnow() + timedelta(hours=4))
        create_calendar_event(
            title=f"Meeting: {subject}",
            start_at=start_time,
            end_at=start_time + timedelta(hours=1),
            event_type="meeting",
            source_email_id=email_id,
        )
        events_created += 1

        create_checklist_task(
            title=f"Prepare for meeting: {subject}",
            due_at=start_time,
            source_email_id=email_id,
            checklist=["Prepare notes", "Carry documents", "Reach cabin on time"],
            priority="high",
        )
        tasks_created += 1

    else:
        create_checklist_task(
            title=f"Review email: {subject}",
            due_at=extracted_time,
            source_email_id=email_id,
            checklist=["Read details", "Decide action"],
            priority="low",
        )
        tasks_created += 1

    notification_message = (
        f"Email processed as '{category}'. Created {tasks_created} task(s) and {events_created} event(s)."
    )
    send_notification_email(to_email=sender, subject=f"Assistant Update: {subject}", message=notification_message)
    notifications_sent += 1

    form_preview = None
    if action_link and category in {"job", "hackathon"}:
        form_preview = autofill_preview(form_url=action_link, context=subject)

    return OrchestrationResult(
        category=category,
        tasks_created=tasks_created,
        events_created=events_created,
        notifications_sent=notifications_sent,
        form_preview=form_preview,
    )


def chat_workflow(message: str) -> str:
    return answer_query(message)


def sync_gmail_inbox_workflow(user_id: str = "default-user", query: str = "newer_than:7d") -> list[OrchestrationResult]:
    messages = fetch_recent_gmail_messages(user_id=user_id, query=query)
    results: list[OrchestrationResult] = []
    for message in messages:
        results.append(
            process_email_workflow(
                email_id=message.get("email_id", ""),
                subject=message.get("subject", ""),
                sender=message.get("sender", ""),
                body=message.get("snippet", "") or message.get("body_hint", ""),
            )
        )
    return results
