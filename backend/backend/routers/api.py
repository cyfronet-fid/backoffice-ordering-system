# pylint: disable=no-member

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, and_, select

from backend.auth import verify_api_key
from backend.db import get_session_dep
from backend.models.tables import (
    Message,
    MessageCreateAPI,
    MessagePublic,
    Order,
    OrderCreateAPI,
    OrderPublic,
    Provider,
    ProviderCreateAPI,
    ProviderPublicWithDetails,
    User,
    UserType,
)

router = APIRouter(prefix="/api", tags=["api"], dependencies=[Depends(verify_api_key)])


@router.post("/providers", response_model=ProviderPublicWithDetails, operation_id="apiCreateProvider")
def create_provider(  # type: ignore
    provider_payload: ProviderCreateAPI,
    session: Annotated[Session, Depends(get_session_dep)],
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
    session: Annotated[Session, Depends(get_session_dep)],
):
    user: User = session.get(User, message_payload.user_id)  # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail=f"User {message_payload.user_id} does not exist.")

    if UserType.MP_USER not in user.user_type:
        raise HTTPException(status_code=400, detail=f"User {message_payload.user_id} is not an MP_USER.")

    order: Order = session.get(Order, message_payload.order_id)  # type: ignore
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {message_payload.order_id} does not exist.")

    db_message = Message(author=user, order=order, content=message_payload.content)

    # Associate the user with the given order if not already associated
    if user not in order.users:
        order.users.append(user)

    session.add_all([db_message, order])
    session.commit()
    session.refresh(db_message)

    return db_message


@router.post("/orders", response_model=OrderPublic, operation_id="apiCreateOrder")
def create_order(  # type: ignore
    order_payload: OrderCreateAPI,
    session: Annotated[Session, Depends(get_session_dep)],
):
    sql = select(Provider).where(
        Provider.id.in_(order_payload.provider_ids),  # type: ignore
    )
    providers = session.scalars(sql).all()

    if len(providers) != len(order_payload.provider_ids):
        found_ids = {p.id for p in providers}
        missing_ids = set(order_payload.provider_ids) - found_ids
        raise HTTPException(status_code=400, detail=f"Providers {list(missing_ids)} do not exist.")

    all_managers = {
        manager for provider in providers for manager in provider.managers
    }  # Associate all managers for every provider with this order

    db_order = Order(**order_payload.model_dump(), providers=providers, users=list(all_managers))

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    return db_order
