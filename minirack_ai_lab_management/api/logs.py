"""System logs endpoints"""
from fastapi import APIRouter, HTTPException
from minirack_ai_lab_management.services.remote import remote_host_service
from minirack_ai_lab_management.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/system/{host}")
async def get_system_logs(host: str, lines: int = 50) -> Dict[str, Any]:
    """Get system logs from a specific host"""
    # Map host names to IPs
    host_map = {
        "laforge": settings.LAFORGE_HOST,
        "data": settings.DATA_HOST,
        "riker": settings.RIKER_HOST,
    }

    target_host = host_map.get(host.lower())
    if not target_host:
        raise HTTPException(status_code=400, detail=f"Unknown host: {host}")

    logs = await remote_host_service.get_system_logs(target_host, "system", lines)
    return {
        "host": host,
        "ip": target_host,
        "logs": logs,
        "line_count": len(logs),
    }


@router.get("/service/{service}")
async def get_service_logs(service: str, lines: int = 50) -> Dict[str, Any]:
    """Get logs for a specific service"""
    service_hosts = {
        "ollama": settings.DATA_HOST,
        "openweb-ui": settings.RIKER_HOST,
        "hermes": settings.RIKER_HOST,
    }

    if service not in service_hosts:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service}")

    target_host = service_hosts[service]
    logs = await remote_host_service.get_system_logs(target_host, service, lines)
    return {
        "service": service,
        "host_ip": target_host,
        "logs": logs,
        "line_count": len(logs),
    }


@router.get("/")
async def get_all_logs(service: str = None, lines: int = 20) -> List[Dict[str, Any]]:
    """Get logs from all services"""
    all_logs = []

    services = ["ollama", "openweb-ui", "hermes"] if not service else [service]

    for svc in services:
        try:
            log_data = await get_service_logs(svc, lines)
            all_logs.append(log_data)
        except Exception as e:
            logger.error(f"Error getting logs for {svc}: {e}")

    return all_logs
