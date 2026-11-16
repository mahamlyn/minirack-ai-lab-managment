"""Dashboard endpoints"""
from fastapi import APIRouter
from typing import List
from minirack_ai_lab_management.models import DashboardData, HostInfo, ServiceInfo
from minirack_ai_lab_management.services.health import health_service
from minirack_ai_lab_management.services.remote import remote_host_service
from minirack_ai_lab_management.config import settings

router = APIRouter()


@router.get("/", response_model=DashboardData)
async def get_dashboard():
    """Get complete dashboard data"""
    # Collect host information
    hosts: List[HostInfo] = []

    # LaForge (ai-utility)
    laforge = await remote_host_service.check_host_health(
        settings.LAFORGE_HOST, "LaForge", "ai-utility"
    )
    hosts.append(laforge)

    # Data (ai-core)
    data = await remote_host_service.check_host_health(
        settings.DATA_HOST, "Data", "ai-core"
    )
    hosts.append(data)

    # Riker (ai-web)
    riker = await remote_host_service.check_host_health(
        settings.RIKER_HOST, "Riker", "ai-web"
    )
    hosts.append(riker)

    # Collect service information
    services: List[ServiceInfo] = []

    # Ollama service
    ollama_status = await remote_host_service.check_service_health(
        "ollama", settings.DATA_HOST, 11434
    )
    services.append(
        ServiceInfo(
            name="ollama",
            host=settings.DATA_HOST,
            status=ollama_status,
            memory_mb=0,
            cpu_percent=0,
            uptime_seconds=0,
            last_check=laforge.last_check,
        )
    )

    # OpenWebUI service
    openweb_status = await remote_host_service.check_service_health(
        "openweb-ui", settings.RIKER_HOST, 8000
    )
    services.append(
        ServiceInfo(
            name="openweb-ui",
            host=settings.RIKER_HOST,
            status=openweb_status,
            memory_mb=0,
            cpu_percent=0,
            uptime_seconds=0,
            last_check=riker.last_check,
        )
    )

    # Get metrics
    current_metrics = await health_service.collect_metrics()

    return DashboardData(
        hosts=hosts,
        services=services,
        models=[],
        recent_metrics=[current_metrics],
        alerts=[],
    )


@router.get("/hosts", response_model=List[HostInfo])
async def get_hosts():
    """Get all hosts status"""
    hosts: List[HostInfo] = []

    laforge = await remote_host_service.check_host_health(
        settings.LAFORGE_HOST, "LaForge", "ai-utility"
    )
    hosts.append(laforge)

    data = await remote_host_service.check_host_health(
        settings.DATA_HOST, "Data", "ai-core"
    )
    hosts.append(data)

    riker = await remote_host_service.check_host_health(
        settings.RIKER_HOST, "Riker", "ai-web"
    )
    hosts.append(riker)

    return hosts


@router.get("/services", response_model=List[ServiceInfo])
async def get_services():
    """Get all services status"""
    services: List[ServiceInfo] = []

    ollama_status = await remote_host_service.check_service_health(
        "ollama", settings.DATA_HOST, 11434
    )
    services.append(
        ServiceInfo(
            name="ollama",
            host=settings.DATA_HOST,
            status=ollama_status,
            memory_mb=0,
            cpu_percent=0,
            uptime_seconds=0,
            last_check=health_service.last_metrics.get("system").last_check,
        )
    )

    openweb_status = await remote_host_service.check_service_health(
        "openweb-ui", settings.RIKER_HOST, 8000
    )
    services.append(
        ServiceInfo(
            name="openweb-ui",
            host=settings.RIKER_HOST,
            status=openweb_status,
            memory_mb=0,
            cpu_percent=0,
            uptime_seconds=0,
            last_check=health_service.last_metrics.get("system").last_check,
        )
    )

    return services
