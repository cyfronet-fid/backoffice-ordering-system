from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.tables import Message

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.get("/", response_model=list[Message], operation_id="readMessages")
def read_messages(session: Annotated[Session, Depends(get_session)]):  # type: ignore
    messages = session.exec(select(Message)).all()
    return messages
