"""Health check endpoints"""
from fastapi import APIRouter
from minirack_ai_lab_management.services.health import health_service
from minirack_ai_lab_management.models import SystemMetrics

router = APIRouter()


@router.get("/", response_model=dict)
async def get_health():
    """Get overall system health"""
    metrics = await health_service.collect_metrics()
    return {
        "status": "healthy" if metrics.cpu_percent < 80 else "warning",
        "timestamp": metrics.timestamp,
        "cpu_percent": metrics.cpu_percent,
        "memory_percent": metrics.memory_percent,
        "disk_percent": metrics.disk_percent,
    }


@router.get("/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get current system metrics"""
    return await health_service.collect_metrics()


@router.get("/live")
async def liveness():
    """Liveness probe"""
    return {"status": "alive"}


@router.get("/ready")
async def readiness():
    """Readiness probe"""
    return {"status": "ready"}
