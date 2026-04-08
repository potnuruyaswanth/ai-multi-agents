from datetime import datetime

from fastapi import APIRouter, Query

from agents.calendar_agent.tools import list_events
from agents.form_agent.tools import autofill_preview
from agents.notification_agent.tools import build_daily_digest
from agents.task_agent.tools import list_tasks
from agents.orchestrator_agent.tools import chat_workflow, process_email_workflow
from api.schemas import (
    ChatRequest,
    ChatResponse,
    FormAutofillRequest,
    ProcessEmailRequest,
    ProcessEmailResponse,
)

router = APIRouter()


@router.post("/process-email", response_model=ProcessEmailResponse)
def process_email(payload: ProcessEmailRequest):
    result = process_email_workflow(
        email_id=payload.email_id,
        subject=payload.subject,
        sender=payload.sender,
        body=payload.body,
    )
    return ProcessEmailResponse(
        category=result["category"],
        tasks_created=result["tasks_created"],
        events_created=result["events_created"],
        notifications_sent=result["notifications_sent"],
    )


@router.get("/tasks")
def get_tasks(start: datetime | None = Query(default=None), end: datetime | None = Query(default=None)):
    tasks = [task.model_dump() for task in list_tasks(start=start, end=end)]
    return {"tasks": tasks}


@router.get("/events")
def get_events(start: datetime | None = Query(default=None), end: datetime | None = Query(default=None)):
    events = [event.model_dump() for event in list_events(start=start, end=end)]
    return {"events": events}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    return ChatResponse(reply=chat_workflow(payload.message))


@router.post("/form/autofill-preview")
def form_autofill(payload: FormAutofillRequest):
    return autofill_preview(form_url=payload.form_url, context=payload.context)


@router.get("/daily-digest")
def daily_digest(user_email: str = Query(default="student@example.com"), user_id: str = Query(default="default-user"), date: datetime | None = Query(default=None)):
    return build_daily_digest(user_email=user_email, user_id=user_id, target_date=date)
