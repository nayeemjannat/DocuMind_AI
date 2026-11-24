import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.worker.__main__ import run_worker_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage optional inline ingestion worker lifecycle when DATABASE_URL is configured."""
    stop_event = threading.Event()
    worker_thread = None

    if settings.DATABASE_URL and settings.ENABLE_INLINE_WORKER:
        worker_thread = threading.Thread(
            target=run_worker_loop,
            args=(stop_event, "inline-web-worker"),
            daemon=True,
        )
        worker_thread.start()

    try:
        yield
    finally:
        if worker_thread is not None:
            stop_event.set()
            worker_thread.join(timeout=2)


def create_application() -> FastAPI:
    """Application factory for DocuMind AI FastAPI service."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
        docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_V1_PREFIX}/redoc" if settings.DEBUG else None,
    )

    # Set up CORS middleware
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(Exception)
    async def safe_unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
        )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
