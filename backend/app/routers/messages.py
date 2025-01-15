from fastapi import APIRouter
from sqlmodel import select

from app.dependencies import SessionDep
from app.models.tables import Message

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
)


@router.get("/", response_model=list[Message], operation_id="readMessages")
def read_messages(session: SessionDep):  # type: ignore
    messages = session.exec(select(Message)).all()
    return messages
