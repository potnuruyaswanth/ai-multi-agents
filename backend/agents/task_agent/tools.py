from __future__ import annotations

from datetime import datetime, timezone

from integrations.tasks_service import create_google_task, list_google_tasks
from database.repository import Repository, new_task


repo = Repository()


def create_checklist_task(
    title: str,
    due_at: datetime | None,
    source_email_id: str | None,
    checklist: list[str],
    priority: str = "medium",
    user_id: str = "default-user",
):
    task = new_task(
        title=title,
        due_at=due_at,
        source_email_id=source_email_id,
        checklist=checklist,
        priority=priority,
    )
    notes = "\n".join([f"- {item}" for item in checklist])
    normalized_due_at = due_at if due_at is None or due_at.tzinfo else due_at.replace(tzinfo=timezone.utc)
    create_google_task(title=title, notes=notes, due_at=normalized_due_at, user_id=user_id)
    return repo.create_task(task)


def list_tasks(start: datetime | None = None, end: datetime | None = None, user_id: str = "default-user"):
    local_tasks = repo.list_tasks(start=start, end=end)
    if start and end:
        remote_tasks = list_google_tasks(user_id=user_id)
        merged = list(local_tasks)
        for remote_task in remote_tasks:
            due_value = remote_task.get("due")
            due_at = None
            if due_value:
                due_at = datetime.fromisoformat(due_value.replace("Z", "+00:00"))
            merged.append(
                new_task(
                    title=remote_task.get("title", "Google Task"),
                    due_at=due_at,
                    source_email_id=None,
                    checklist=[remote_task.get("notes", "")],
                    priority="medium",
                )
            )
        return merged
    return local_tasks


def sync_local_tasks_to_google(user_id: str = "default-user") -> dict:
    local_tasks = repo.list_tasks()
    synced = 0
    for task in local_tasks:
        create_google_task(
            title=task.title,
            notes="\n".join(task.checklist) if task.checklist else task.description,
            due_at=task.due_at if task.due_at is None or task.due_at.tzinfo else task.due_at.replace(tzinfo=timezone.utc),
            user_id=user_id,
        )
        synced += 1
    return {"synced": synced}
