from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

import backend.services.call_whitelabel as wl
from backend.auth import current_user
from backend.const import ORDER_STATUS_STATE_MACHINE
from backend.db import get_session_dep
from backend.models.tables import MessagePublic, Order, OrderPublic, OrderPublicWithProviders, OrderStatus, User

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
    order: Order = session.get(Order, order_id)  # type: ignore
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not user.has_access_to_order(order):
        raise HTTPException(status_code=403, detail="You do not have access to this order")

    return order


@router.get("/", response_model=list[OrderPublicWithProviders], operation_id="readOrders")
def read_orders(  # type: ignore
    session: Annotated[Session, Depends(get_session_dep)],
    user: Annotated[User, Depends(current_user)],
):
    if user.is_admin() or user.is_coordinator():
        return session.exec(select(Order)).all()

    if user.is_provider_manager():
        return user.orders

    return []


@router.get("/{order_id}", response_model=OrderPublicWithProviders, operation_id="getOrderById")
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
):
    if new_status not in ORDER_STATUS_STATE_MACHINE[order.status]:
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = new_status

    session.add(order)
    session.commit()
    session.refresh(order)

    order_id: int = order.id  # type: ignore
    background_tasks.add_task(wl.change_order_status, order_id=order_id)

    return order
