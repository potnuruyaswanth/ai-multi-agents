from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Productivity Assistant"
    api_prefix: str = "/api/v1"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "ai_productivity_assistant"
    storage_backend: str = "mongodb"
    firestore_project_id: str = ""
    firestore_database_id: str = "(default)"
    firestore_credentials_path: str = ""

    gmail_credentials_path: str = ""
    google_calendar_credentials_path: str = ""
    google_drive_credentials_path: str = ""
    google_project_id: str = ""
    google_location: str = "us-central1"
    vertex_model: str = "gemini-2.5-flash"

    google_oauth_client_config_path: str = ""
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    notification_sender_email: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
