import logging
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.middleware import SecurityHeadersMiddleware
from backend.routers import api, messages, orders, providers, root, users
from backend.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    swagger_ui_init_oauth={
        "clientId": get_settings().keycloak_client_id,
        "realm": get_settings().keycloak_realm,
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid profile email",
    }
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled server error", exc_info=exc, extra={"request_meta": {"method": request.method, "url": str(request.url)}})
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"}
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
