from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import messages, orders, providers, users

app = FastAPI()
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(providers.router)
app.include_router(messages.router)

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
