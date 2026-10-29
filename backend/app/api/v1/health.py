from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness_probe() -> dict:
    """Liveness probe indicating the process is alive."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe() -> dict:
    """Readiness probe indicating service can accept work."""
    # In P03/P04, database/storage checks will be connected here
    return {"status": "ready"}
