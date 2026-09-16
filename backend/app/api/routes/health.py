from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Liveness check — confirms the API is up."""
    return {"status": "ok"}
