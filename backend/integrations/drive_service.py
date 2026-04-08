from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build

from integrations.google_oauth import load_credentials


def _drive_service(user_id: str = "default-user"):
    credentials = load_credentials("drive", user_id)
    if not credentials:
        return None
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def list_google_drive_files(user_id: str = "default-user", query: str = "trashed=false", max_results: int = 25) -> list[dict[str, Any]]:
    service = _drive_service(user_id)
    if service is None:
        return []

    response = (
        service.files()
        .list(
            q=query,
            pageSize=max_results,
            fields="files(id,name,mimeType,webViewLink,webContentLink,modifiedTime,iconLink)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )
    return response.get("files", [])


def application_asset_links(user_id: str = "default-user") -> list[dict[str, Any]]:
    files = list_google_drive_files(user_id=user_id)
    assets: list[dict[str, Any]] = []
    for file in files:
        name = (file.get("name") or "").lower()
        mime_type = file.get("mimeType") or ""
        if any(keyword in name for keyword in ["resume", "cv", "portfolio", "cover letter", "transcript", "certificate"]) or mime_type in {
            "application/pdf",
            "application/vnd.google-apps.document",
        }:
            assets.append(
                {
                    "id": file.get("id"),
                    "name": file.get("name"),
                    "mimeType": mime_type,
                    "webViewLink": file.get("webViewLink"),
                    "webContentLink": file.get("webContentLink"),
                }
            )
    return assets
