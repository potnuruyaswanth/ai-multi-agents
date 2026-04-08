from __future__ import annotations

from fastapi import APIRouter, Query

from config.settings import get_settings
from integrations.google_oauth import connection_status

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get("/checklist")
def setup_checklist(user_id: str = Query(default="default-user")):
    settings = get_settings()

    oauth_client_configured = bool(
        settings.google_oauth_client_config_path
        or (settings.google_oauth_client_id and settings.google_oauth_client_secret)
    )

    storage_backend = settings.storage_backend.lower()
    firestore_ready = storage_backend != "firestore" or bool(settings.firestore_project_id)

    smtp_ready = bool(settings.smtp_user and settings.smtp_password)

    providers = {
        "gmail": connection_status("gmail", user_id),
        "calendar": connection_status("calendar", user_id),
        "tasks": connection_status("tasks", user_id),
        "drive": connection_status("drive", user_id),
    }

    checklist = {
        "oauth_client_configured": oauth_client_configured,
        "redirect_uri": settings.google_oauth_redirect_uri,
        "storage_backend": storage_backend,
        "firestore_ready": firestore_ready,
        "smtp_ready": smtp_ready,
        "providers": providers,
    }

    checklist["ready_for_live_run"] = (
        checklist["oauth_client_configured"]
        and checklist["providers"]["gmail"]["connected"]
        and checklist["providers"]["calendar"]["connected"]
        and checklist["providers"]["tasks"]["connected"]
        and checklist["providers"]["drive"]["connected"]
        and checklist["firestore_ready"]
    )

    return checklist
