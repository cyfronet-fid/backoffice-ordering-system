from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.auth import current_user
from backend.db import get_session
from backend.models.tables import Message, MessageCreate, MessagePublic, User

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.get("/", response_model=list[MessagePublic], operation_id="readMessages")
def read_messages(session: Annotated[Session, Depends(get_session)]):  # type: ignore
    messages = session.exec(select(Message)).all()
    return messages


@router.post("/", response_model=MessagePublic, operation_id="createMessage")
def create_message(  # type: ignore
    message: MessageCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_message = Message(
        content=message.content,
        order_id=message.order_id,
        author_id=user.id,
    )

    try:
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409) from e

    return db_message
