from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from config.settings import get_settings
from database.repository import Repository


GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TASKS_SCOPES = ["https://www.googleapis.com/auth/tasks"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

repo = Repository()


@dataclass(frozen=True)
class OAuthState:
    provider: str
    user_id: str

    def encode(self) -> str:
        raw = json.dumps({"provider": self.provider, "user_id": self.user_id})
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode(state: str) -> "OAuthState":
        raw = base64.urlsafe_b64decode(state.encode("utf-8")).decode("utf-8")
        data = json.loads(raw)
        return OAuthState(provider=data["provider"], user_id=data["user_id"])


def _client_config() -> dict[str, Any]:
    settings = get_settings()
    if settings.google_oauth_client_config_path:
        with open(settings.google_oauth_client_config_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    if settings.google_oauth_client_id and settings.google_oauth_client_secret:
        return {
            "web": {
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_oauth_redirect_uri],
            }
        }

    raise RuntimeError(
        "Missing Google OAuth client configuration. Set GOOGLE_OAUTH_CLIENT_CONFIG_PATH or GOOGLE_OAUTH_CLIENT_ID/SECRET."
    )


def create_flow(provider: str, state: OAuthState) -> Flow:
    if provider == "gmail":
        scopes = GMAIL_SCOPES
    elif provider == "calendar":
        scopes = CALENDAR_SCOPES
    elif provider == "tasks":
        scopes = TASKS_SCOPES
    elif provider == "drive":
        scopes = DRIVE_SCOPES
    else:
        raise ValueError("Unsupported provider")
    flow = Flow.from_client_config(_client_config(), scopes=scopes, state=state.encode())
    settings = get_settings()
    flow.redirect_uri = settings.google_oauth_redirect_uri
    return flow


def authorization_url(provider: str, user_id: str) -> dict[str, str]:
    state = OAuthState(provider=provider, user_id=user_id)
    flow = create_flow(provider, state)
    url, oauth_state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state.encode(),
    )
    return {"authorization_url": url, "state": oauth_state}


def exchange_code(code: str, state: str) -> dict[str, Any]:
    parsed_state = OAuthState.decode(state)
    flow = create_flow(parsed_state.provider, parsed_state)
    flow.fetch_token(code=code)
    credentials = flow.credentials
    account_email = get_account_email(credentials, parsed_state.provider)
    save_credentials(parsed_state.provider, parsed_state.user_id, credentials, account_email)
    return {
        "provider": parsed_state.provider,
        "user_id": parsed_state.user_id,
        "account_email": account_email,
        "scopes": credentials.scopes or [],
    }


def credentials_to_payload(credentials: Credentials) -> dict[str, Any]:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or []),
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }


def payload_to_credentials(payload: dict[str, Any]) -> Credentials:
    return Credentials(
        token=payload.get("token"),
        refresh_token=payload.get("refresh_token"),
        token_uri=payload.get("token_uri"),
        client_id=payload.get("client_id"),
        client_secret=payload.get("client_secret"),
        scopes=payload.get("scopes"),
    )


def save_credentials(provider: str, user_id: str, credentials: Credentials, account_email: str | None = None) -> None:
    document = {
        "provider": provider,
        "user_id": user_id,
        "account_email": account_email,
        "credentials": credentials_to_payload(credentials),
        "updated_at": datetime.now(timezone.utc),
    }
    repo.save_oauth_connection(document)


def load_credentials(provider: str, user_id: str) -> Credentials | None:
    document = repo.get_oauth_connection(provider=provider, user_id=user_id)
    if not document:
        return None

    credentials = payload_to_credentials(document["credentials"])
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(provider, user_id, credentials, document.get("account_email"))
    return credentials


def get_account_email(credentials: Credentials, provider: str) -> str | None:
    try:
        if provider == "gmail":
            from googleapiclient.discovery import build

            service = build("gmail", "v1", credentials=credentials, cache_discovery=False)
            profile = service.users().getProfile(userId="me").execute()
            return profile.get("emailAddress")
        if provider == "calendar":
            return None
    except Exception:
        return None
    return None


def credentials_ready(provider: str, user_id: str) -> bool:
    return load_credentials(provider, user_id) is not None


def connection_status(provider: str, user_id: str) -> dict[str, Any]:
    document = repo.get_oauth_connection(provider=provider, user_id=user_id)
    credentials = load_credentials(provider, user_id)
    return {
        "provider": provider,
        "user_id": user_id,
        "connected": credentials is not None,
        "account_email": document.get("account_email") if document else None,
        "scopes": list(credentials.scopes or []) if credentials else [],
        "updated_at": document.get("updated_at") if document else None,
    }
