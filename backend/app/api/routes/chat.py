from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageResponse, ChatSessionCreate, ChatSessionResponse, ChatStreamRequest
from app.services.chat_service import (
    build_assistant_reply,
    create_session,
    delete_session,
    get_session_for_user,
    list_messages,
    list_sessions,
    save_message,
    stream_sse_tokens,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def create_chat_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSessionResponse:
    session = create_session(db, current_user, payload.title)
    return ChatSessionResponse.model_validate(session)


@router.get("/sessions", response_model=list[ChatSessionResponse])
def read_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSessionResponse]:
    return [ChatSessionResponse.model_validate(session) for session in list_sessions(db, current_user)]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def read_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessageResponse]:
    session = get_session_for_user(db, current_user, session_id)
    return [ChatMessageResponse.model_validate(message) for message in list_messages(db, session)]


@router.delete("/sessions/{session_id}", status_code=204)
def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    session = get_session_for_user(db, current_user, session_id)
    delete_session(db, session)


@router.post("/sessions/{session_id}/stream")
def stream_chat_reply(
    session_id: int,
    payload: ChatStreamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    session = get_session_for_user(db, current_user, session_id)
    save_message(db, session, "user", payload.message)
    assistant_reply = build_assistant_reply(payload.message)
    save_message(db, session, "assistant", assistant_reply)
    return StreamingResponse(stream_sse_tokens(assistant_reply), media_type="text/event-stream")
