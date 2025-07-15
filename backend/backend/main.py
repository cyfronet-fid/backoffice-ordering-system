from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routers import api, messages, orders, providers, users

app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": get_settings().keycloak_client_id,
        "realm": get_settings().keycloak_realm,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid profile email",
    }
)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(providers.router)
app.include_router(messages.router)
app.include_router(api.router)


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Any) -> Any:
    response = await call_next(request)

    # Content Security Policy - prevents XSS attacks
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to FastAPI backend!"}
