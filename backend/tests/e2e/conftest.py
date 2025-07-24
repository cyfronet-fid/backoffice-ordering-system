import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, delete
from testcontainers.postgres import PostgresContainer

# Set default config at module level to avoid import issues
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")
os.environ.setdefault("DB_NAME", "postgres")
os.environ.setdefault("API_KEY", "test-api-key")

postgres_container = PostgresContainer("postgres:16-alpine")


@pytest.fixture(scope="module", autouse=True)
def setup_test_db(request):
    postgres_container.start()

    # Override database config for tests
    os.environ["DB_HOST"] = postgres_container.get_container_host_ip()
    os.environ["DB_PORT"] = str(postgres_container.get_exposed_port(5432))
    os.environ["DB_USER"] = postgres_container.username
    os.environ["DB_PASSWORD"] = postgres_container.password
    os.environ["DB_NAME"] = postgres_container.dbname

    def cleanup():
        postgres_container.stop()

    request.addfinalizer(cleanup)


@pytest.fixture(scope="module")
def test_engine(setup_test_db):
    from backend.config import get_settings

    settings = get_settings()
    engine = create_engine(settings.db_connection_string)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture(scope="module")
def client(setup_test_db):
    from backend.main import app

    return TestClient(app)


@pytest.fixture
def db_session(test_engine):
    with Session(test_engine) as session:
        yield session


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    with Session(test_engine) as session:
        # Clean all tables in correct order (respecting foreign key constraints)
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(delete(table))
        session.commit()
    yield


@pytest.fixture
def api_headers():
    return {"x-key": "test-api-key"}
