from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.auth import current_user
from backend.db import get_session
from backend.models.tables import User, UserCreate, UserPublic, UserPublicWithEmployers

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(current_user)],
)


@router.get("/", response_model=list[UserPublic], operation_id="readUsers")
def read_users(session: Annotated[Session, Depends(get_session)]):  # type: ignore
    users = session.exec(select(User)).all()
    return users


@router.get("/me", response_model=UserPublic, operation_id="getCurrentUser")
def get_current_user(user: Annotated[User, Depends(current_user)]):  # type: ignore
    return user


@router.get("/{user_id}", response_model=UserPublicWithEmployers, operation_id="getUserById")
def get_user_by_id(user_id: int, session: Annotated[Session, Depends(get_session)]):  # type: ignore
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserPublic, operation_id="createUser")
def create_user(user: UserCreate, session: Annotated[Session, Depends(get_session)]):  # type: ignore
    db_user = User.model_validate(user)

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already exists") from e

    return db_user
