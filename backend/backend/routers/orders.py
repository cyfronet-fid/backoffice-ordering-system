from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.const import ORDER_STATUS_STATE_MACHINE
from backend.db import get_session
from backend.models.tables import MessagePublic, Order, OrderPublic, OrderPublicWithProviders, OrderStatus

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/", response_model=list[OrderPublicWithProviders], operation_id="readOrders")
def read_orders(session: Annotated[Session, Depends(get_session)]):  # type: ignore
    orders = session.exec(select(Order)).all()
    return orders


@router.get("/{order_id}", response_model=OrderPublicWithProviders, operation_id="getOrderById")
def get_order_by_id(order_id: int, session: Annotated[Session, Depends(get_session)]):  # type: ignore
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}/messages", response_model=list[MessagePublic], operation_id="getOrderMessages")
def get_order_messages(order_id: int, session: Annotated[Session, Depends(get_session)]):  # type: ignore
    # TODO: Below might be non-ideal in terms of performance - probably it's best to sort in SQL
    return sorted(get_order_by_id(order_id, session).messages, key=lambda message: message.created_at)


@router.post("/{order_id}/change_status", response_model=OrderPublic, operation_id="changeOrderStatus")
def change_order_status(  # type: ignore
    order_id: int,
    new_status: OrderStatus,
    session: Annotated[Session, Depends(get_session)],
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if new_status not in ORDER_STATUS_STATE_MACHINE[order.status]:
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = new_status

    session.add(order)
    session.commit()
    session.refresh(order)

    return order
