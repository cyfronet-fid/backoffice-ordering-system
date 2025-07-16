import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_api_key():
    return "test-api-key"


@pytest.fixture(scope="session")
def client(test_api_key):
    # This is a missing piece in our configuration, that is purposely left blank for security reasons
    os.environ.setdefault("API_KEY", test_api_key)

    from backend.main import app

    yield TestClient(app)
