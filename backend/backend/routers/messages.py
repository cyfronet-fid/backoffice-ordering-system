from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session, select

import backend.services.call_whitelabel as wl
from backend.auth import current_user
from backend.db import get_session_dep
from backend.models.tables import Message, MessageCreate, MessagePublic, MessageScope, User, UserType

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    dependencies=[Depends(current_user)],
)


@router.get("/", response_model=list[MessagePublic], operation_id="readMessages")
def read_messages(session: Annotated[Session, Depends(get_session_dep)]):  # type: ignore
    messages = session.exec(select(Message)).all()
    return messages


@router.post("/", response_model=MessagePublic, operation_id="createMessage")
def create_message(  # type: ignore
    message: MessageCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session_dep)],
    background_tasks: BackgroundTasks,
):
    db_message = Message(
        content=message.content,
        order_id=message.order_id,
        author_id=user.id,
        scope=message.scope,
    )

    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    if message.scope == MessageScope.PUBLIC:
        message_id: int = db_message.id  # type: ignore
        background_tasks.add_task(
            wl.post_message,
            message_id=message_id,
            # TODO: adjust according to frontend view - for now the "strongest" (coordinator) role takes precedent
            send_as=UserType.COORDINATOR if UserType.COORDINATOR in user.user_type else UserType.PROVIDER_MANAGER,
        )

    return db_message
