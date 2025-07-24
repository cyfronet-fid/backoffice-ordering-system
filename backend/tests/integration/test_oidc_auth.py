from unittest.mock import MagicMock, patch

import jwt
import pytest


@pytest.fixture
def example_jwt():
    # It's a toy JWT - not leaking anything here!
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"


@pytest.fixture
def protected_oidc_path():
    return "/users/me"


def test_missing_token(client, protected_oidc_path):
    response = client.get(protected_oidc_path)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_invalid_header_format(client, protected_oidc_path):
    response = client.get(protected_oidc_path, headers={"authorization": "bad format"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication token format"}


def test_invalid_format(client, protected_oidc_path):
    response = client.get(protected_oidc_path, headers={"authorization": f"Bearer invalid"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_invalid_token(client, example_jwt, protected_oidc_path):
    with patch("backend.auth.jwks_client") as mock_jwks_client:
        mock_jwks_client.get_signing_key_from_jwt.side_effect = jwt.InvalidTokenError("Invalid token")

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}


def test_valid_token(client, example_jwt):
    # Test successful JWT token parsing without database interaction
    # This test focuses on the JWT validation logic, not endpoint behavior
    with patch("backend.auth.jwks_client") as mock_jwks_client, patch("backend.auth.jwt.decode") as mock_decode:

        # Mock successful JWT validation
        mock_signing_key = MagicMock()
        mock_signing_key.key = "mock-key"
        mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

        # Mock decoded JWT payload
        mock_decode.return_value = {"sub": "user123", "email": "test@example.com", "name": "Test User"}

        # Import and test the verify_token function directly
        from backend.auth import verify_token

        result = verify_token(f"Bearer {example_jwt}")

        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
