from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.db import get_session_dep
from backend.main import app


@pytest.fixture
def client():
    # Override DB session with a mock so unit tests never touch a real database.
    # Integration tests supply a real session via their own conftest.
    app.dependency_overrides[get_session_dep] = lambda: MagicMock()
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_session_dep, None)
