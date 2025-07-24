from unittest.mock import patch

import pytest


@pytest.fixture
def protected_api_path():
    return "/api/providers"


def test_api_key_not_present(client, protected_api_path):
    response = client.post(protected_api_path)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_api_key_invalid(client, protected_api_path):
    response = client.post(protected_api_path, headers={"x-key": "example"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API Key"}


def test_api_key_valid(client, protected_api_path, test_api_key):
    response = client.post(protected_api_path, headers={"x-key": test_api_key})
    assert response.status_code not in [401, 403]
