import re
import ssl
from secrets import compare_digest
from typing import Annotated, Any

import certifi
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, OpenIdConnect
from sqlmodel import Session, select

from backend.config import get_settings
from backend.db import get_session_dep
from backend.models.tables import User, UserType

oidc_scheme = OpenIdConnect(openIdConnectUrl=get_settings().keycloak_connection_string)
header_scheme = APIKeyHeader(name="x-key")

jwks_client = jwt.PyJWKClient(
    uri=get_settings().keycloak_jwks_uri,
    ssl_context=(ssl.create_default_context(cafile=certifi.where())),
)

BEARER_PATTERN = re.compile(r"^Bearer ([A-Za-z0-9\-_.]+)$")


def verify_token(raw_token: Annotated[str, Depends(oidc_scheme)]) -> dict[str, Any]:
    match = BEARER_PATTERN.match(raw_token)
    if not match:
        raise HTTPException(status_code=401, detail="Invalid authentication token format")

    token = match.group(1)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            jwt=token,
            key=signing_key,
            audience=get_settings().keycloak_client_id,
            issuer=get_settings().keycloak_realm_base_url,
            algorithms=["RS256"],
            leeway=5,  # KeyCloak's clock is mismatched +/- 5 seconds
        )

        return payload

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


def verify_api_key(api_key: str = Depends(header_scheme)) -> None:
    expected_key = get_settings().api_key
    if not api_key or not compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )


def current_user(
    token: Annotated[dict[str, Any], Depends(verify_token)], session: Annotated[Session, Depends(get_session_dep)]
) -> User:
    name = token["name"]
    email = token["email"]

    query = select(User).where(User.email == email)
    user = session.exec(query).first()

    if user is None:
        user = User(
            name=name,
            email=email,
            user_type=[UserType.MP_USER],
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    return user
