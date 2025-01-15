from fastapi import APIRouter
from sqlmodel import select

from app.dependencies import SessionDep
from app.models.tables import Provider

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
)


@router.get("/", response_model=list[Provider], operation_id="readProviders")
def read_providers(session: SessionDep):  # type: ignore
    providers = session.exec(select(Provider)).all()
    return providers
