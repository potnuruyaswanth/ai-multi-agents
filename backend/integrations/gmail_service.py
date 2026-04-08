from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build

from integrations.google_oauth import load_credentials


def _gmail_service(user_id: str = "default-user"):
    credentials = load_credentials("gmail", user_id)
    if not credentials:
        return None
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


def _extract_headers(payload: dict[str, Any]) -> dict[str, str]:
    headers = payload.get("headers", [])
    return {header.get("name", ""): header.get("value", "") for header in headers}


def list_inbox_messages(user_id: str = "default-user", query: str = "newer_than:7d", max_results: int = 10) -> list[dict[str, Any]]:
    service = _gmail_service(user_id)
    if service is None:
        return []

    response = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = response.get("messages", [])
    results: list[dict[str, Any]] = []

    for message in messages:
        message_detail = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
        payload = message_detail.get("payload", {})
        headers = _extract_headers(payload)
        body_text = ""

        if payload.get("parts"):
            for part in payload["parts"]:
                body_text = part.get("body", {}).get("data", "") or body_text
        else:
            body_text = payload.get("body", {}).get("data", "")

        results.append(
            {
                "email_id": message_detail.get("id"),
                "thread_id": message_detail.get("threadId"),
                "subject": headers.get("Subject", ""),
                "sender": headers.get("From", ""),
                "snippet": message_detail.get("snippet", ""),
                "body_hint": body_text,
                "internal_date": message_detail.get("internalDate"),
            }
        )
    return results


def get_message_details(message_id: str, user_id: str = "default-user") -> dict[str, Any] | None:
    service = _gmail_service(user_id)
    if service is None:
        return None
    message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = message.get("payload", {})
    headers = _extract_headers(payload)
    return {
        "email_id": message.get("id"),
        "thread_id": message.get("threadId"),
        "subject": headers.get("Subject", ""),
        "sender": headers.get("From", ""),
        "snippet": message.get("snippet", ""),
        "payload": payload,
    }
