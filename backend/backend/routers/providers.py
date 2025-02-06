from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.tables import Provider

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
)


@router.get("/", response_model=list[Provider], operation_id="readProviders")
def read_providers(session: Annotated[Session, Depends(get_session)]):  # type: ignore
    providers = session.exec(select(Provider)).all()
    return providers
