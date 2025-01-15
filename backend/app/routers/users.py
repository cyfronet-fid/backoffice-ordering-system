from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.dependencies import SessionDep
from app.models.tables import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=list[User], operation_id="readUsers")
def read_users(session: SessionDep):  # type: ignore
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=User, operation_id="getUserById")
def get_user_by_id(user_id: int, session: SessionDep):  # type: ignore
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
