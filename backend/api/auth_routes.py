from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from integrations.google_oauth import authorization_url, exchange_code

router = APIRouter(prefix="/auth/google", tags=["google-auth"])


@router.get("/{provider}/url")
def get_authorization_link(provider: str, user_id: str = Query(default="default-user")):
    if provider not in {"gmail", "calendar", "tasks", "drive"}:
        raise HTTPException(status_code=400, detail="Provider must be gmail, calendar, tasks, or drive")
    return authorization_url(provider=provider, user_id=user_id)


@router.get("/callback")
def google_callback(code: str, state: str, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=error)
    return exchange_code(code=code, state=state)
