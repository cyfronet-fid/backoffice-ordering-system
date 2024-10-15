from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session

from app.config import get_settings


def get_session() -> Generator[Session, None, None]:
    engine = create_engine(get_settings().db_connection_string)
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
