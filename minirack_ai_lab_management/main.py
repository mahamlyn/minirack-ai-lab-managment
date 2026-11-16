"""
MiniRack AI Lab Management Portal
Main application entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from minirack_ai_lab_management.config import settings
from minirack_ai_lab_management.api import router
from minirack_ai_lab_management.services.health import health_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🚀 Starting MiniRack AI Lab Management Portal")
    await health_service.initialize()
    yield
    # Shutdown
    logger.info("🛑 Shutting down MiniRack AI Lab Management Portal")
    await health_service.close()


# Create FastAPI application
app = FastAPI(
    title="MiniRack AI Lab Management",
    description="Performance monitoring and configuration portal for MiniRack AI Lab",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# API routes
app.include_router(router.router, prefix="/api/v1")

# Static files (frontend)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "minirack-ai-lab-management"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "minirack_ai_lab_management.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
