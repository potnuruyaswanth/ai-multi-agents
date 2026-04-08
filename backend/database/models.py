from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str = Field(default="default-user")
    name: str = "Student User"
    email: EmailStr = "student@example.com"
    resume_link: Optional[str] = None
    drive_resume_link: Optional[str] = None
    drive_resource_links: list[str] = Field(default_factory=list)
    portfolio_link: Optional[str] = None


class EmailRecord(BaseModel):
    email_id: str
    subject: str
    sender: str
    body: str
    category: Literal["job", "hackathon", "meeting", "event", "other"] = "other"
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed_status: Literal["new", "processed", "error"] = "new"
    metadata: dict = Field(default_factory=dict)


class Task(BaseModel):
    task_id: str
    title: str
    description: str = ""
    due_at: Optional[datetime] = None
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: Literal["low", "medium", "high"] = "medium"
    source_email_id: Optional[str] = None
    checklist: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(BaseModel):
    event_id: str
    title: str
    start_at: datetime
    end_at: datetime
    type: Literal["meeting", "hackathon", "deadline", "event", "assessment"] = "event"
    location: str = ""
    source_email_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Notification(BaseModel):
    notification_id: str
    to_email: EmailStr
    subject: str
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
