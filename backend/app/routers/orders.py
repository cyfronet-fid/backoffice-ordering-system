from fastapi import APIRouter
from sqlmodel import select

from app.dependencies import SessionDep
from app.models.tables import Order

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/", response_model=list[Order], operation_id="readOrders")
def read_orders(session: SessionDep):  # type: ignore
    orders = session.exec(select(Order)).all()
    return orders
