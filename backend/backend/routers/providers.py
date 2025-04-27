from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth import current_user
from backend.db import get_session_dep
from backend.models.tables import Provider, ProviderPublic, ProviderPublicWithDetails

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
    dependencies=[Depends(current_user)],
)


@router.get("/", response_model=list[ProviderPublic], operation_id="readProviders")
def read_providers(session: Annotated[Session, Depends(get_session_dep)]):  # type: ignore
    providers = session.exec(select(Provider)).all()
    return providers


@router.get("/{provider_id}", response_model=ProviderPublicWithDetails, operation_id="getProviderById")
def get_user_by_id(provider_id: int, session: Annotated[Session, Depends(get_session_dep)]):  # type: ignore
    provider = session.get(Provider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
