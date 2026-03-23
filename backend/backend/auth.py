import re
import ssl
from secrets import compare_digest
from typing import Annotated, Any

import certifi
import httpx
import jwt
from cachetools import TTLCache, cached
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, OpenIdConnect
from sqlalchemy.exc import IntegrityError
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

http_client = httpx.Client(verify=ssl.create_default_context(cafile=certifi.where()))

BEARER_PATTERN = re.compile(r"^Bearer ([A-Za-z0-9\-_.]+)$")


@cached(TTLCache(maxsize=256, ttl=300), key=lambda raw_auth, _sub: _sub)
def _fetch_userinfo(raw_auth: str, _sub: str) -> dict[str, Any]:
    try:
        response = http_client.get(
            get_settings().keycloak_userinfo_uri,
            headers={"Authorization": raw_auth},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=401, detail="Token rejected by UserInfo endpoint") from e
    except httpx.RequestError:
        return {}


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
    raw_auth: Annotated[str, Depends(oidc_scheme)],
    token: Annotated[dict[str, Any], Depends(verify_token)],
    session: Annotated[Session, Depends(get_session_dep)],
) -> User:
    name = token.get("name")
    email = token.get("email")

    try:
        if not name or not email:
            userinfo = _fetch_userinfo(raw_auth, token["sub"])
            name = userinfo["name"]
            email = userinfo["email"]

    except KeyError as exc:
        raise HTTPException(status_code=401, detail="Unable to determine user identity") from exc

    query = select(User).where(User.email == email)
    user = session.exec(query).first()

    if user is None:
        try:
            user = User(
                name=name,
                email=email,
                user_type=[UserType.MP_USER],
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        except IntegrityError as exc:
            session.rollback()
            user = session.exec(select(User).where(User.email == email)).first()
            if user is None:
                raise HTTPException(status_code=500, detail="Failed to create user") from exc

    return user
