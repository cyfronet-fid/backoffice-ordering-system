from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import tickets

app = FastAPI()
app.include_router(tickets.router)

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
