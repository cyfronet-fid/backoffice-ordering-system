from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.tables import Order

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/", response_model=list[Order], operation_id="readOrders")
def read_orders(session: Annotated[Session, Depends(get_session)]):  # type: ignore
    orders = session.exec(select(Order)).all()
    return orders
