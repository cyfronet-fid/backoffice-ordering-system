from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth import current_user
from backend.db import get_session_dep
from backend.models.tables import User, UserPublic, UserPublicWithEmployers

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(current_user)],
)


def _get_user_with_access_check(
    user_id: int,
    session: Annotated[Session, Depends(get_session_dep)],
    this_user: Annotated[User, Depends(current_user)],
) -> User:
    target_user: User = session.get(User, user_id)  # type: ignore
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    if not this_user.has_access_to_other_user(target_user):
        raise HTTPException(status_code=403, detail=f"You do not have access to user {user_id}")

    return target_user


@router.get("/", response_model=list[UserPublic], operation_id="readUsers")
def read_users(  # type: ignore
    session: Annotated[Session, Depends(get_session_dep)],
    this_user: Annotated[User, Depends(current_user)],
):
    if this_user.is_admin() or this_user.is_coordinator():
        return session.exec(select(User)).all()

    return [this_user]


@router.get("/me", response_model=UserPublic, operation_id="getCurrentUser")
def get_current_user(this_user: Annotated[User, Depends(current_user)]):  # type: ignore
    return this_user


@router.get("/{user_id}", response_model=UserPublicWithEmployers, operation_id="getUserById")
def get_user_by_id(target_user: Annotated[User, Depends(_get_user_with_access_check)]):  # type: ignore
    return target_user
