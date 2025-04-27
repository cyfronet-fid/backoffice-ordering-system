from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlmodel import Session

from backend.config import get_settings

engine = create_engine(get_settings().db_connection_string)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_session_dep() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session
