from fastapi import APIRouter

router = APIRouter(prefix="")


@router.get("/")
def health_check() -> dict[str, str]:
    return {"message": "Welcome to FastAPI backend!"}
