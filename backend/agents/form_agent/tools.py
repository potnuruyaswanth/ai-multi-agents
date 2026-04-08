from __future__ import annotations

from integrations.drive_service import application_asset_links
from database.models import User


DEFAULT_PROFILE = User(
    id="default-user",
    name="Student User",
    email="student@example.com",
    resume_link="https://example.com/resume.pdf",
)


def autofill_preview(form_url: str, context: str = "", user_id: str = "default-user") -> dict:
    drive_assets = application_asset_links(user_id=user_id)
    resume_asset = next((asset for asset in drive_assets if "resume" in (asset.get("name") or "").lower()), None)
    resource_links = [asset.get("webViewLink") for asset in drive_assets if asset.get("webViewLink")]

    return {
        "form_url": form_url,
        "suggested_data": {
            "full_name": DEFAULT_PROFILE.name,
            "email": DEFAULT_PROFILE.email,
            "resume_link": resume_asset.get("webViewLink") if resume_asset else DEFAULT_PROFILE.drive_resume_link or DEFAULT_PROFILE.resume_link,
            "resource_links": resource_links or DEFAULT_PROFILE.drive_resource_links,
            "context": context,
        },
        "attachments": drive_assets,
        "requires_user_confirmation": True,
        "next_step": "Preview values and submit manually with one click.",
    }
