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


def test_valid_token(client, example_jwt, protected_oidc_path):
    with (
        patch("backend.auth.jwks_client") as mock_jwks_client,
        patch("backend.auth.jwt.decode") as mock_jwt_decode,
    ):

        mock_signing_key = MagicMock()
        mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

        mock_jwt_decode.return_value = {
            "sub": "1234567890",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "admin": True,
            "iat": 1516239022,
        }

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})

        assert response.status_code not in [401, 403]


def test_expired_token(client, example_jwt, protected_oidc_path):
    with (
        patch("backend.auth.jwks_client") as mock_jwks_client,
        patch("backend.auth.jwt.decode") as mock_jwt_decode,
    ):
        mock_signing_key = MagicMock()
        mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})

        assert response.status_code == 401
        assert response.json() == {"detail": "Token has expired"}
