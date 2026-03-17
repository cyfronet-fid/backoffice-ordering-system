import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

import backend.services.call_whitelabel as wl
from backend.auth import current_user
from backend.const import ORDER_STATUS_STATE_MACHINE
from backend.db import get_session_dep
from backend.models.tables import MessagePublic, Order, OrderPublic, OrderPublicWithDetails, OrderStatus, User
from backend.routers.users import get_current_user
from backend.services import email_notifications
from backend.utils import group_users_by_role

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(current_user)],
)


def _get_order_with_access_check(
    order_id: int,
    session: Annotated[Session, Depends(get_session_dep)],
    user: Annotated[User, Depends(current_user)],
) -> Order:
    statement = select(Order).where(Order.id == order_id).options(selectinload(Order.messages))  # type: ignore
    order = session.scalars(statement).one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    if not user.has_access_to_order(order):
        raise HTTPException(status_code=403, detail=f"You do not have access to order {order_id}")

    return order


@router.get("/", response_model=list[OrderPublicWithDetails], operation_id="readOrders")
def read_orders(  # type: ignore
    session: Annotated[Session, Depends(get_session_dep)],
    user: Annotated[User, Depends(current_user)],
):
    if user.is_admin() or user.is_coordinator():
        orders = session.exec(select(Order).order_by(Order.created_at.desc())).all()  # type: ignore # pylint: disable=no-member
        return orders

    if user.is_provider_manager():
        return sorted(user.orders, key=lambda order: order.created_at, reverse=True)

    return []


@router.get("/{order_id}", response_model=OrderPublicWithDetails, operation_id="getOrderById")
def get_order_by_id(order: Annotated[Order, Depends(_get_order_with_access_check)]):  # type: ignore
    return order


@router.get("/{order_id}/messages", response_model=list[MessagePublic], operation_id="getOrderMessages")
def get_order_messages(order: Annotated[Order, Depends(_get_order_with_access_check)]):  # type: ignore
    return sorted(order.messages, key=lambda message: message.created_at)


@router.post("/{order_id}/change_status", response_model=OrderPublic, operation_id="changeOrderStatus")
def change_order_status(  # type: ignore
    order: Annotated[Order, Depends(_get_order_with_access_check)],
    new_status: OrderStatus,
    session: Annotated[Session, Depends(get_session_dep)],
    background_tasks: BackgroundTasks,
    status_change_author: Annotated[User, Depends(get_current_user)]
):
    if new_status not in ORDER_STATUS_STATE_MACHINE[order.status]:
        raise HTTPException(status_code=400, detail=f"Invalid status transition: {order.status} -> {new_status.name}")

    status_from = order.status
    # order.status = new_status
    print(f"Changing order status to {new_status}")

    session.add(order)
    session.commit()
    session.refresh(order)

    order_id: int = order.id  # type: ignore
    # background_tasks.add_task(wl.change_order_status, order_id=order_id)
    logging.error(f"\t\t\t\ttest logging")

    # users = _resolve_order_users(order)

    grouped_users = group_users_by_role(order)
    print(f"admin: {[user.email for user in grouped_users["admin"]]}")
    print(f"coordinator: {[user.email for user in grouped_users["coordinator"]]}")
    print(f"provider_manager: {[user.email for user in grouped_users["provider_manager"]]}")
    print(f"mp_user: {[user.email for user in grouped_users["mp_user"]]}")


    print()

    # background_tasks.add_task(
    #     email_notifications.send_order_status_change_notification,
    #     order_id=order_id,
    #     status_from=status_from,
    #     status_to=new_status,
    #     users=grouped_users,
    #     status_change_author=status_change_author,
    # )

    email_notifications.send_order_status_change_notification(order_id=order_id, status_from=status_from, status_to=new_status, users=grouped_users, status_change_author=status_change_author)

    return order
