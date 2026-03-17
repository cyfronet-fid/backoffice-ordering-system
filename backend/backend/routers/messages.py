from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

import backend.services.call_whitelabel as wl
from backend.auth import current_user
from backend.db import get_session_dep
from backend.models.tables import Message, MessageCreate, MessagePublic, MessageScope, Order, User, UserType
from backend.services.email_notifications import send_order_message_notification
from backend.utils import get_whitelabel_role, _resolve_message_recipients

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    dependencies=[Depends(current_user)],
)


# def _resolve_message_recipient(order: Order, scope: MessageScope) -> list[User]:
#     allowed_roles: set[UserType]
#
#     if scope == MessageScope.PUBLIC:
#         allowed_roles = {UserType.COORDINATOR, UserType.PROVIDER_MANAGER, UserType.MP_USER}
#     else:
#         allowed_roles = {UserType.COORDINATOR, UserType.PROVIDER_MANAGER}
#
#     return [u for u in order.users if any(role in allowed_roles for role in u.user_type)]


@router.post("/", response_model=MessagePublic, operation_id="createMessage")
def create_message(  # type: ignore
    message: MessageCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session_dep)],
    background_tasks: BackgroundTasks,
):
    order: Order = session.get(Order, message.order_id)  # type: ignore

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {message.order_id} not found")

    if not user.has_access_to_order(order):
        raise HTTPException(status_code=403, detail=f"You cannot create messages for order {message.order_id}")

    db_message = Message(
        content=message.content,
        order_id=message.order_id,
        author_id=user.id,
        scope=message.scope,
    )

    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    recipients = _resolve_message_recipients(order, message.scope)
    print("\t\t\tRecipients:")
    for recipient in recipients:
        print(f"\t\t\t{recipient.email}")
    # print(recipients)

    # if message.scope == MessageScope.PUBLIC:
    #     # send email to everyone, providers, coordinators and users
    #     message_id: int = db_message.id  # type: ignore
    #     background_tasks.add_task(
    #         wl.post_message,
    #         message_id=message_id,
    #         send_as=get_whitelabel_role(user),
    #     )
    # else:
        # send email to providers and coordinators, not users

    background_tasks.add_task(
        send_order_message_notification,
        message_id=db_message.id,
        recipients=recipients,
    )

    return db_message
