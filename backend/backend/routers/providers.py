from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.auth import current_user
from backend.db import get_session_dep
from backend.models.tables import Provider, ProviderPublic, ProviderPublicWithDetails, User

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
    dependencies=[Depends(current_user)],
)


def _get_provider_with_access_check(
    provider_id: int,
    session: Annotated[Session, Depends(get_session_dep)],
    user: Annotated[User, Depends(current_user)],
) -> Provider:
    provider: Provider = session.get(Provider, provider_id)  # type: ignore
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    if not user.has_access_to_provider(provider):
        raise HTTPException(status_code=403, detail="You do not have access to this provider")

    return provider


@router.get("/", response_model=list[ProviderPublic], operation_id="readProviders")
def read_providers(  # type: ignore
    session: Annotated[Session, Depends(get_session_dep)], user: Annotated[User, Depends(current_user)]
):
    if user.is_admin() or user.is_coordinator():
        return session.exec(select(Provider)).all()

    if user.is_provider_manager():
        return user.employers

    return []


@router.get("/{provider_id}", response_model=ProviderPublicWithDetails, operation_id="getProviderById")
def get_provider_by_id(provider: Annotated[Provider, Depends(_get_provider_with_access_check)]):  # type: ignore
    return provider
