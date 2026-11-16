"""Main API router"""
from fastapi import APIRouter
from minirack_ai_lab_management.api import dashboard, health, config, models, logs

router = APIRouter()

# Include sub-routers
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(config.router, prefix="/config", tags=["Configuration"])
router.include_router(models.router, prefix="/models", tags=["Models"])
router.include_router(logs.router, prefix="/logs", tags=["Logs"])
