from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProcessEmailRequest(BaseModel):
    email_id: str
    subject: str
    sender: str
    body: str
    received_at: Optional[datetime] = None


class ProcessEmailResponse(BaseModel):
    category: str
    tasks_created: int = 0
    events_created: int = 0
    notifications_sent: int = 0


class ChatRequest(BaseModel):
    message: str = Field(min_length=2)


class ChatResponse(BaseModel):
    reply: str


class FormAutofillRequest(BaseModel):
    form_url: str
    context: str = ""
