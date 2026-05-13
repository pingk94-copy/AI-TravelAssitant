from collections.abc import Iterable

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.models.user import User


def create_session(db: Session, user: User, title: str) -> ChatSession:
    session = ChatSession(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, user: User) -> list[ChatSession]:
    return list(db.scalars(select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.created_at.desc())))


def get_session_for_user(db: Session, user: User, session_id: int) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session


def list_messages(db: Session, session: ChatSession) -> list[ChatMessage]:
    return list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at, ChatMessage.id)
        )
    )


def save_message(db: Session, session: ChatSession, role: str, content: str) -> ChatMessage:
    message = ChatMessage(session_id=session.id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def build_assistant_reply(user_message: str) -> str:
    return (
        "I received your travel request: "
        f"{user_message}. "
        "For the current learning phase, I can outline the trip intent and keep the conversation history. "
        "The next AI phase will replace this local reply with a real streaming model response."
    )


def stream_sse_tokens(text: str) -> Iterable[str]:
    for token in text.split(" "):
        yield f"event: token\ndata: {token} \n\n"
    yield "event: done\ndata: [DONE]\n\n"
