# pylint: disable=no-member

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, and_, select

from backend.auth import verify_api_key
from backend.db import get_session
from backend.models.tables import (
    Message,
    MessageCreateAPI,
    MessagePublic,
    Order,
    OrderCreate,
    OrderPublic,
    Provider,
    ProviderCreate,
    ProviderPublicWithDetails,
    User,
    UserType,
)

router = APIRouter(prefix="/api", tags=["api"], dependencies=[Depends(verify_api_key)])


@router.post("/providers", response_model=ProviderPublicWithDetails, operation_id="apiCreateProvider")
def create_provider(  # type: ignore
    provider_payload: ProviderCreate,
    session: Annotated[Session, Depends(get_session)],
):
    sql = select(User).where(
        and_(
            User.id.in_(provider_payload.manager_ids),  # type: ignore
            User.user_type.contains([UserType.PROVIDER_MANAGER]),  # type: ignore
        )
    )

    db_managers = session.scalars(sql).all()

    if len(db_managers) != len(provider_payload.manager_ids):
        found_ids = {m.id for m in db_managers}
        missing_ids = set(provider_payload.manager_ids) - found_ids
        raise HTTPException(
            status_code=400, detail=f"Managers {list(missing_ids)} are either missing or not provider managers."
        )

    db_provider = Provider(name=provider_payload.name, website=provider_payload.website, managers=db_managers)

    try:
        session.add(db_provider)
        session.commit()
        session.refresh(db_provider)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail="Provider already exists") from e

    return db_provider


@router.post("/messages", response_model=MessagePublic, operation_id="apiCreateMessage")
def create_message(  # type: ignore
    message_payload: MessageCreateAPI,
    session: Annotated[Session, Depends(get_session)],
):
    user = session.get(User, message_payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {message_payload.user_id} does not exist.")

    if UserType.MP_USER not in user.user_type:
        raise HTTPException(status_code=400, detail=f"User {message_payload.user_id} is not an MP_USER.")

    order = session.get(Order, message_payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {message_payload.order_id} does not exist.")

    db_message = Message(author=user, order=order, content=message_payload.content)

    session.add(db_message)
    session.commit()
    session.refresh(db_message)

    return db_message


@router.post("/orders", response_model=OrderPublic, operation_id="apiCreateOrder")
def create_order(  # type: ignore
    order_payload: OrderCreate,
    session: Annotated[Session, Depends(get_session)],
):
    db_order = Order(**order_payload.model_dump())

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    return db_order
