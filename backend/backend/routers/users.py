from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from backend.dependencies import SessionDep
from backend.models.tables import User, UserCreate, UserPublic

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


@router.post("/", response_model=UserPublic, operation_id="createUser")
def create_user(user: UserCreate, session: SessionDep):  # type: ignore
    db_user = User.model_validate(user)

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=409) from e

    return db_user
