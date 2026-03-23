from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException

from backend.db import get_session_dep
from backend.main import app
from backend.models.tables import User, UserType


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
    # JWT contains name + email — no UserInfo call needed
    fake_user = User(name="John Doe", email="john.doe@example.com", user_type=[UserType.MP_USER])
    fake_user.id = 1

    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = fake_user
    app.dependency_overrides[get_session_dep] = lambda: mock_session

    try:
        with (
            patch("backend.auth.jwks_client") as mock_jwks_client,
            patch("backend.auth.jwt.decode") as mock_jwt_decode,
        ):
            mock_jwks_client.get_signing_key_from_jwt.return_value = MagicMock()
            mock_jwt_decode.return_value = {
                "sub": "1234567890",
                "name": "John Doe",
                "email": "john.doe@example.com",
            }

            response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
            assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_session_dep, None)


def test_concurrent_first_login_race_condition(client, example_jwt, protected_oidc_path):
    from sqlalchemy.exc import IntegrityError

    fake_user = User(name="John Doe", email="john.doe@example.com", user_type=[UserType.MP_USER])
    fake_user.id = 42

    mock_session = MagicMock()
    mock_session.exec.return_value.first.side_effect = [None, fake_user]
    mock_session.commit.side_effect = IntegrityError("duplicate", {}, Exception())
    app.dependency_overrides[get_session_dep] = lambda: mock_session

    with (
        patch("backend.auth.jwks_client") as mock_jwks_client,
        patch("backend.auth.jwt.decode") as mock_jwt_decode,
    ):
        mock_jwks_client.get_signing_key_from_jwt.return_value = MagicMock()
        mock_jwt_decode.return_value = {
            "sub": "1234567890",
            "name": "John Doe",
            "email": "john.doe@example.com",
        }

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
        assert response.status_code not in [401, 403, 500]
        mock_session.rollback.assert_called_once()


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


def test_jwt_without_claims_falls_back_to_userinfo(client, example_jwt, protected_oidc_path):
    # JWT has no name/email (second Keycloak deployment) — UserInfo is called
    fake_user = User(name="Jane Doe", email="jane@example.com", user_type=[UserType.MP_USER])
    fake_user.id = 2

    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = fake_user
    app.dependency_overrides[get_session_dep] = lambda: mock_session

    try:
        with (
            patch("backend.auth.jwks_client") as mock_jwks_client,
            patch("backend.auth.jwt.decode") as mock_jwt_decode,
            patch("backend.auth._fetch_userinfo") as mock_userinfo,
        ):
            mock_jwks_client.get_signing_key_from_jwt.return_value = MagicMock()
            mock_jwt_decode.return_value = {"sub": "008318ae-88e6-4f61-b7a2-a186bb95f476@access.eosc.pl"}
            mock_userinfo.return_value = {"name": "Jane Doe", "email": "jane@example.com"}

            response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
            assert response.status_code == 200
            mock_userinfo.assert_called_once()
    finally:
        app.dependency_overrides.pop(get_session_dep, None)


def test_userinfo_missing_email_raises_401(client, example_jwt, protected_oidc_path):
    with (
        patch("backend.auth.jwks_client") as mock_jwks_client,
        patch("backend.auth.jwt.decode") as mock_jwt_decode,
        patch(
            "backend.auth._fetch_userinfo",
            return_value={"name": "Jane Doe"},  # no email
        ),
    ):
        mock_jwks_client.get_signing_key_from_jwt.return_value = MagicMock()
        mock_jwt_decode.return_value = {"sub": "some-sub"}  # no name/email in JWT

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Unable to determine user identity"}


def test_userinfo_network_failure_raises_401(client, example_jwt, protected_oidc_path):
    with (
        patch("backend.auth.jwks_client") as mock_jwks_client,
        patch("backend.auth.jwt.decode") as mock_jwt_decode,
        patch(
            "backend.auth._fetch_userinfo",
            return_value={},  # network failure returns empty dict
        ),
    ):
        mock_jwks_client.get_signing_key_from_jwt.return_value = MagicMock()
        mock_jwt_decode.return_value = {"sub": "some-sub"}  # no name/email in JWT

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
        assert response.status_code == 401


def test_userinfo_token_rejected_raises_401(client, example_jwt, protected_oidc_path):
    with (
        patch("backend.auth.jwks_client") as mock_jwks_client,
        patch("backend.auth.jwt.decode") as mock_jwt_decode,
        patch(
            "backend.auth._fetch_userinfo",
            side_effect=HTTPException(status_code=401, detail="Token rejected by UserInfo endpoint"),
        ),
    ):
        mock_jwks_client.get_signing_key_from_jwt.return_value = MagicMock()
        mock_jwt_decode.return_value = {"sub": "some-sub"}  # no name/email in JWT

        response = client.get(protected_oidc_path, headers={"authorization": f"Bearer {example_jwt}"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Token rejected by UserInfo endpoint"}


def test_userinfo_cached_by_sub():
    from backend.auth import _fetch_userinfo

    _fetch_userinfo.cache.clear()

    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "Jane", "email": "jane@example.com"}

    with patch("backend.auth.http_client.get", return_value=mock_response) as mock_get:
        result1 = _fetch_userinfo("Bearer token-v1", "sub-abc")
        result2 = _fetch_userinfo("Bearer token-v2", "sub-abc")  # refreshed token, same sub

        assert mock_get.call_count == 1  # second call hit the cache
        assert result1 == result2

    _fetch_userinfo.cache.clear()
