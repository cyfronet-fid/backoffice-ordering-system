from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.middleware import SecurityHeadersMiddleware
from backend.routers import api, messages, orders, providers, root, users

app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": get_settings().keycloak_client_id,
        "realm": get_settings().keycloak_realm,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid profile email",
    }
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(users.router)
app.include_router(providers.router)
app.include_router(messages.router)
app.include_router(api.router)
app.include_router(root.router)
