# pylint: disable=no-member

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

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
    UserCreate,
    UserPublic,
    UserType,
)

router = APIRouter(prefix="/api", tags=["api"], dependencies=[Depends(verify_api_key)])


@router.post("/providers", response_model=ProviderPublicWithDetails, operation_id="apiCreateProvider")
def create_provider(  # type: ignore
    provider_payload: ProviderCreateAPI,
    session: Annotated[Session, Depends(get_session_dep)],
):
    # TODO: Ignore the mail mapping for now
    # sql = select(User).where(
    #     and_(
    #         User.email.in_(provider_payload.manager_emails),  # type: ignore
    #         User.user_type.contains([UserType.PROVIDER_MANAGER]),  # type: ignore
    #     )
    # )
    #
    # db_managers = session.scalars(sql).all()
    #
    # if len(db_managers) != len(provider_payload.manager_emails):
    #     found_emails = {m.email for m in db_managers}
    #     missing_emails = set(provider_payload.manager_emails) - found_emails
    #     raise HTTPException(
    #         status_code=400, detail=f"Managers {list(missing_emails)} are either missing or not provider managers."
    #     )

    db_provider = Provider(
        **provider_payload.model_dump(),
        # managers=db_managers,
    )

    try:
        session.add(db_provider)
        session.commit()
        session.refresh(db_provider)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"Provider {provider_payload.pid} already exists") from e

    return db_provider


@router.post("/users", response_model=UserPublic, operation_id="apiCreateUser")
def create_user(user_payload: UserCreate, session: Annotated[Session, Depends(get_session_dep)]):  # type: ignore
    db_user = User(**user_payload.model_dump())

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"User {user_payload.email} already exists") from e

    return db_user


@router.post("/messages", response_model=MessagePublic, operation_id="apiCreateMessage")
def create_message(  # type: ignore
    message_payload: MessageCreateAPI,
    session: Annotated[Session, Depends(get_session_dep)],
):
    user = session.scalars(select(User).where(User.email == message_payload.user_email)).first()

    if not user:
        raise HTTPException(status_code=404, detail=f"User {message_payload.user_email} does not exist.")

    if UserType.MP_USER not in user.user_type:
        raise HTTPException(status_code=400, detail=f"User {message_payload.user_email} is not an MP_USER.")

    order = session.scalars(
        select(Order).where(
            Order.external_ref == message_payload.order_external_ref,
            Order.project_ref == message_payload.project_external_ref,
        )
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {message_payload.order_external_ref} does not exist.")

    db_message = Message(
        content=message_payload.content,
        scope=message_payload.scope,
        author_id=user.id,
        order_id=order.id,
    )

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
    sql = select(Provider).where(Provider.pid.in_(order_payload.provider_pids))  # type: ignore
    providers = session.scalars(sql).all()

    if len(providers) != len(order_payload.provider_pids):
        found_pids = {p.pid for p in providers}
        missing_pids = set(order_payload.provider_pids) - found_pids
        raise HTTPException(status_code=400, detail=f"Providers {list(missing_pids)} do not exist.")

    owner = session.scalars(select(User).where(User.email == order_payload.owner_email)).first()
    if not owner or UserType.MP_USER not in owner.user_type:
        raise HTTPException(
            status_code=400, detail=f"User {order_payload.owner_email} does not exist or is not an MP_USER."
        )

    # Associate all managers for every provider with this order
    unique_managers = list({manager for provider in providers for manager in provider.managers})

    db_order = Order(**order_payload.model_dump(), providers=providers, users=unique_managers + [owner])

    try:
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409, detail=f"Order {order_payload.project_ref}/{order_payload.external_ref} already exists"
        ) from e

    return db_order
