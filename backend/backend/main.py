from fastapi import FastAPI
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

app.add_middleware(
    CORSMiddleware,
    # TODO: Restrict origin to an exact frontend url (based on env) once I know the DNS
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to FastAPI backend!"}
