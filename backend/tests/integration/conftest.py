import inspect

import pytest
from alembic import command
from alembic.config import Config
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from pytest_factoryboy import register
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import create_engine, text
from sqlmodel import Session, SQLModel

import tests.integration.factories as _factories_module
from backend.config import get_settings
from backend.db import get_session_dep
from backend.main import app

# Connects to an already-running Postgres — Docker locally, service container in CI.
# get_settings() is called at import time; this is safe because pytest-env
# (pyproject.toml [tool.pytest.ini_options].env) injects test values before
# collection.  Do NOT import this conftest from outside the integration suite.
_settings = get_settings()
postgresql_noproc = factories.postgresql_noproc(
    host=_settings.db_host,
    port=_settings.db_port,
    user=_settings.db_user,
    password=_settings.db_password,
)

_ALL_FACTORIES = [
    cls
    for _, cls in inspect.getmembers(_factories_module, inspect.isclass)
    if issubclass(cls, SQLAlchemyModelFactory) and cls is not SQLAlchemyModelFactory
]

# Register factories as pytest fixtures.
# Each call creates two fixtures: the model instance (e.g. `user`) and the
# factory class (e.g. `user_factory`) for building customized instances.
for _factory in _ALL_FACTORIES:
    register(_factory)


@pytest.fixture(scope="session")
def pg_engine(postgresql_noproc):
    db_name = get_settings().db_name
    with DatabaseJanitor(
        user=postgresql_noproc.user,
        host=postgresql_noproc.host,
        port=postgresql_noproc.port,
        dbname=db_name,
        version=postgresql_noproc.version,
        password=postgresql_noproc.password,
    ):
        connection_str = (
            f"postgresql+psycopg://{postgresql_noproc.user}:{postgresql_noproc.password}"
            f"@{postgresql_noproc.host}:{postgresql_noproc.port}/{db_name}"
        )
        engine = create_engine(connection_str)

        alembic_cfg = Config("alembic.ini")
        with engine.begin() as connection:
            alembic_cfg.attributes["connection"] = connection
            command.upgrade(alembic_cfg, "head")

        yield engine
        engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(pg_engine):
    """Clean BEFORE the test so a failing test leaves data in the DB for inspection.

    This is autouse so it runs before any per-test fixture (including
    pytest-factoryboy fixtures like ``user`` / ``provider``) — guaranteeing
    that factory-created rows are never truncated by a late-running cleanup.
    """
    with Session(pg_engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
        session.commit()
    yield


@pytest.fixture
def db_session(pg_engine, clean_tables):
    with Session(pg_engine) as session:
        yield session


@pytest.fixture
def client(db_session):
    # Inject the same session the test uses so setup data is immediately visible
    # to the app without needing an explicit commit.
    app.dependency_overrides[get_session_dep] = lambda: db_session
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_session_dep, None)


@pytest.fixture(autouse=True)
def bind_factories(db_session):
    # Bind the test's session to every factory so .create() / SubFactory
    # use the same transaction as the test itself.
    for f in _ALL_FACTORIES:
        f._meta.sqlalchemy_session = db_session
    yield
    for f in _ALL_FACTORIES:
        f._meta.sqlalchemy_session = None
