from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness_probe() -> dict:
    """Liveness probe indicating the process is alive."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe() -> dict:
    """Readiness probe indicating service can accept work."""
    # Database and storage health checks will be evaluated here
    return {"status": "ready"}
