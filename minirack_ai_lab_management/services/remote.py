"""Remote host monitoring service"""
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from minirack_ai_lab_management.models import HostInfo, HostStatus, ServiceInfo, ServiceStatus
from minirack_ai_lab_management.config import settings

logger = logging.getLogger(__name__)


class RemoteHostService:
    """Service for monitoring remote hosts"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=5)

    async def initialize(self):
        """Initialize the remote host service"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self):
        """Close the remote host service"""
        if self.session:
            await self.session.close()

    async def check_host_health(self, host: str, name: str, role: str) -> HostInfo:
        """Check health of a remote host via HTTP endpoint"""
        try:
            if self.session is None:
                raise RuntimeError("Service not initialized")

            url = f"http://{host}:9100/metrics"  # Prometheus node exporter
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.text()
                    metrics = self._parse_node_metrics(data)
                    return HostInfo(
                        name=name,
                        ip_address=host,
                        status=self._determine_remote_status(metrics),
                        role=role,
                        uptime_seconds=metrics.get("uptime_seconds", 0),
                        cpu_percent=metrics.get("cpu_percent", 0),
                        memory_percent=metrics.get("memory_percent", 0),
                        disk_percent=metrics.get("disk_percent", 0),
                        temperature_celsius=metrics.get("temperature", None),
                        last_check=datetime.now(),
                    )
        except Exception as e:
            logger.error(f"Error checking host {host}: {e}")

        return HostInfo(
            name=name,
            ip_address=host,
            status=HostStatus.OFFLINE,
            role=role,
            uptime_seconds=0,
            cpu_percent=0,
            memory_percent=0,
            disk_percent=0,
            last_check=datetime.now(),
        )

    async def check_service_health(
        self, service_name: str, host: str, check_port: int
    ) -> ServiceStatus:
        """Check if a service is running and responding"""
        try:
            if self.session is None:
                raise RuntimeError("Service not initialized")

            url = f"http://{host}:{check_port}/health"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return ServiceStatus.RUNNING
        except asyncio.TimeoutError:
            logger.warning(f"Timeout checking {service_name} on {host}:{check_port}")
            return ServiceStatus.ERROR
        except Exception as e:
            logger.debug(f"Error checking {service_name}: {e}")
            return ServiceStatus.ERROR

        return ServiceStatus.UNKNOWN

    async def get_ollama_models(self) -> List[Dict[str, Any]]:
        """Get list of Ollama models from ai-core"""
        try:
            if self.session is None:
                raise RuntimeError("Service not initialized")

            url = f"{settings.OLLAMA_API_HOST}/api/tags"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("models", [])
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")

        return []

    async def get_system_logs(self, host: str, service: str, lines: int = 50) -> List[str]:
        """Get recent system logs from a remote host"""
        try:
            if self.session is None:
                raise RuntimeError("Service not initialized")

            url = f"http://{host}:9100/logs?service={service}&lines={lines}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.error(f"Error getting logs from {host}: {e}")

        return []

    def _parse_node_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """Parse Prometheus node exporter metrics"""
        result = {
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "uptime_seconds": 0,
        }

        for line in metrics_text.split("\n"):
            if line.startswith("#"):
                continue

            if "node_cpu_seconds_total" in line and "mode" not in line:
                try:
                    value = float(line.split()[-1])
                    result["cpu_percent"] = min(100, (value % 100))
                except (ValueError, IndexError):
                    pass

            elif "node_memory_MemAvailable_bytes" in line:
                try:
                    available = float(line.split()[-1])
                    total = self._get_total_memory(metrics_text)
                    if total > 0:
                        result["memory_percent"] = ((total - available) / total) * 100
                except (ValueError, IndexError):
                    pass

            elif "node_filesystem_avail_bytes" in line and 'mountpoint="/"' in line:
                try:
                    avail = float(line.split()[-1])
                    size = self._get_filesystem_size(metrics_text)
                    if size > 0:
                        result["disk_percent"] = ((size - avail) / size) * 100
                except (ValueError, IndexError):
                    pass

            elif "node_boot_time_seconds" in line:
                try:
                    boot_time = float(line.split()[-1])
                    result["uptime_seconds"] = datetime.now().timestamp() - boot_time
                except (ValueError, IndexError):
                    pass

        return result

    def _get_total_memory(self, metrics_text: str) -> float:
        """Extract total memory from metrics"""
        for line in metrics_text.split("\n"):
            if "node_memory_MemTotal_bytes" in line:
                try:
                    return float(line.split()[-1])
                except (ValueError, IndexError):
                    pass
        return 0

    def _get_filesystem_size(self, metrics_text: str) -> float:
        """Extract filesystem size from metrics"""
        for line in metrics_text.split("\n"):
            if "node_filesystem_size_bytes" in line and 'mountpoint="/"' in line:
                try:
                    return float(line.split()[-1])
                except (ValueError, IndexError):
                    pass
        return 0

    def _determine_remote_status(self, metrics: Dict[str, Any]) -> HostStatus:
        """Determine remote host status based on metrics"""
        cpu = metrics.get("cpu_percent", 0)
        memory = metrics.get("memory_percent", 0)
        disk = metrics.get("disk_percent", 0)

        if cpu > 90 or memory > 90 or disk > 90:
            return HostStatus.ERROR
        elif cpu > 70 or memory > 70 or disk > 80:
            return HostStatus.WARNING
        return HostStatus.HEALTHY


import asyncio

remote_host_service = RemoteHostService()
