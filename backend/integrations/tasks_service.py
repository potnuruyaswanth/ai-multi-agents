from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from googleapiclient.discovery import build

from integrations.google_oauth import load_credentials


def _tasks_service(user_id: str = "default-user"):
    credentials = load_credentials("tasks", user_id)
    if not credentials:
        return None
    return build("tasks", "v1", credentials=credentials, cache_discovery=False)


def list_google_task_lists(user_id: str = "default-user") -> list[dict[str, Any]]:
    service = _tasks_service(user_id)
    if service is None:
        return []
    response = service.tasklists().list(maxResults=20).execute()
    return response.get("items", [])


def get_default_task_list_id(user_id: str = "default-user") -> str | None:
    lists = list_google_task_lists(user_id=user_id)
    if not lists:
        return None
    return lists[0].get("id")


def create_google_task(
    title: str,
    notes: str = "",
    due_at: datetime | None = None,
    user_id: str = "default-user",
    tasklist_id: str | None = None,
) -> dict[str, Any] | None:
    service = _tasks_service(user_id)
    if service is None:
        return None

    list_id = tasklist_id or get_default_task_list_id(user_id)
    if list_id is None:
        created_list = service.tasklists().insert(body={"title": "AI Productivity Assistant"}).execute()
        list_id = created_list.get("id")

    payload: dict[str, Any] = {"title": title, "notes": notes or f"Created by AI Productivity Assistant at {datetime.now(timezone.utc).isoformat()}"}
    if due_at is not None:
        payload["due"] = due_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    return service.tasks().insert(tasklist=list_id, body=payload).execute()


def list_google_tasks(user_id: str = "default-user", tasklist_id: str | None = None, max_results: int = 50) -> list[dict[str, Any]]:
    service = _tasks_service(user_id)
    if service is None:
        return []

    list_id = tasklist_id or get_default_task_list_id(user_id)
    if list_id is None:
        return []

    response = service.tasks().list(tasklist=list_id, maxResults=max_results, showCompleted=True, showDeleted=False).execute()
    return response.get("items", [])
