from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any

from config.settings import get_settings
from database.models import EmailRecord, Event, Notification, Task
from database.db import MongoConnection

try:
    from google.cloud import firestore
except Exception:  # pragma: no cover
    firestore = None


class Repository:
    def __init__(self) -> None:
        settings = get_settings()
        self.backend = settings.storage_backend.lower()
        self._firestore_client = None

        if self.backend == "firestore":
            self._firestore_client = self._create_firestore_client(settings)
        else:
            self.db = MongoConnection.get_db()
            self.tasks = self.db["tasks"]
            self.events = self.db["events"]
            self.emails = self.db["emails"]
            self.notifications = self.db["notifications"]
            self.oauth_connections = self.db["oauth_connections"]

    def _create_firestore_client(self, settings):
        if firestore is None:
            raise RuntimeError("google-cloud-firestore is not installed")

        project_id = settings.firestore_project_id or settings.google_project_id
        if settings.firestore_credentials_path:
            return firestore.Client.from_service_account_json(settings.firestore_credentials_path, project=project_id or None)
        if project_id:
            return firestore.Client(project=project_id, database=settings.firestore_database_id or "(default)")
        return firestore.Client(database=settings.firestore_database_id or "(default)")

    def _firestore_collection(self, name: str):
        return self._firestore_client.collection(name)

    def _match_document(self, document: dict[str, Any], filters: dict[str, Any]) -> bool:
        return all(document.get(key) == value for key, value in filters.items())

    def _list_documents(self, collection_name: str) -> list[dict[str, Any]]:
        if self.backend == "firestore":
            return [snapshot.to_dict() or {} for snapshot in self._firestore_collection(collection_name).stream()]
        return [document for document in self.db[collection_name].find({})]

    def save_oauth_connection(self, document: dict[str, Any]) -> None:
        if self.backend == "firestore":
            key = f"{document['provider']}:{document['user_id']}"
            self._firestore_collection("oauth_connections").document(key).set(document)
            return
        self.oauth_connections.update_one(
            {"provider": document["provider"], "user_id": document["user_id"]},
            {"$set": document},
            upsert=True,
        )

    def get_oauth_connection(self, provider: str, user_id: str) -> dict[str, Any] | None:
        if self.backend == "firestore":
            snapshot = self._firestore_collection("oauth_connections").document(f"{provider}:{user_id}").get()
            return snapshot.to_dict() if snapshot.exists else None
        return self.oauth_connections.find_one({"provider": provider, "user_id": user_id})

    def save_email(self, email: EmailRecord) -> EmailRecord:
        document = email.model_dump()
        if self.backend == "firestore":
            self._firestore_collection("emails").document(email.email_id).set(document)
        else:
            self.emails.update_one({"email_id": email.email_id}, {"$set": document}, upsert=True)
        return email

    def create_task(self, task: Task) -> Task:
        document = task.model_dump()
        if self.backend == "firestore":
            self._firestore_collection("tasks").document(task.task_id).set(document)
        else:
            self.tasks.insert_one(document)
        return task

    def list_tasks(self, start: datetime | None = None, end: datetime | None = None) -> list[Task]:
        if self.backend == "firestore":
            docs = self._list_documents("tasks")
        else:
            query: dict = {}
            if start or end:
                query["due_at"] = {}
                if start:
                    query["due_at"]["$gte"] = start
                if end:
                    query["due_at"]["$lte"] = end
            docs = list(self.tasks.find(query).sort("due_at", 1))

        filtered_docs: list[dict[str, Any]] = []
        for document in docs:
            due_at = document.get("due_at")
            if start and due_at and due_at < start:
                continue
            if end and due_at and due_at > end:
                continue
            filtered_docs.append(document)
        return [Task(**document) for document in filtered_docs]

    def create_event(self, event: Event) -> Event:
        document = event.model_dump()
        if self.backend == "firestore":
            self._firestore_collection("events").document(event.event_id).set(document)
        else:
            self.events.insert_one(document)
        return event

    def list_events(self, start: datetime | None = None, end: datetime | None = None) -> list[Event]:
        if self.backend == "firestore":
            docs = self._list_documents("events")
        else:
            query: dict = {}
            if start or end:
                query["start_at"] = {}
                if start:
                    query["start_at"]["$gte"] = start
                if end:
                    query["start_at"]["$lte"] = end
            docs = list(self.events.find(query).sort("start_at", 1))

        filtered_docs: list[dict[str, Any]] = []
        for document in docs:
            start_at = document.get("start_at")
            if start and start_at and start_at < start:
                continue
            if end and start_at and start_at > end:
                continue
            filtered_docs.append(document)
        return [Event(**document) for document in filtered_docs]

    def create_notification(self, notification: Notification) -> Notification:
        document = notification.model_dump()
        if self.backend == "firestore":
            self._firestore_collection("notifications").document(notification.notification_id).set(document)
        else:
            self.notifications.insert_one(document)
        return notification


def new_task(
    title: str,
    due_at: datetime | None,
    source_email_id: str | None,
    checklist: list[str],
    priority: str = "medium",
) -> Task:
    return Task(
        task_id=str(uuid4()),
        title=title,
        due_at=due_at,
        source_email_id=source_email_id,
        checklist=checklist,
        priority=priority,
    )


def new_event(
    title: str,
    start_at: datetime,
    end_at: datetime | None = None,
    event_type: str = "event",
    source_email_id: str | None = None,
) -> Event:
    end_time = end_at or (start_at + timedelta(hours=1))
    return Event(
        event_id=str(uuid4()),
        title=title,
        start_at=start_at,
        end_at=end_time,
        type=event_type,
        source_email_id=source_email_id,
    )


def new_notification(to_email: str, subject: str, message: str) -> Notification:
    return Notification(notification_id=str(uuid4()), to_email=to_email, subject=subject, message=message)
