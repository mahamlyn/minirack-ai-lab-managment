"""Health monitoring and system information service"""
import psutil
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from minirack_ai_lab_management.models import HostInfo, HostStatus, SystemMetrics

logger = logging.getLogger(__name__)


class HealthService:
    """Service for monitoring host and system health"""

    def __init__(self):
        self.last_metrics: Dict[str, SystemMetrics] = {}
        self.monitoring_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize the health service"""
        logger.info("Initializing health service")
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def close(self):
        """Close the health service"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Health service closed")

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage("/").percent,
            network_io_bytes=float(psutil.net_io_counters().bytes_sent),
            network_errors=psutil.net_io_counters().errin + psutil.net_io_counters().errout,
        )
        self.last_metrics["system"] = metrics
        return metrics

    async def get_local_host_info(self, name: str, role: str) -> HostInfo:
        """Get local host information"""
        try:
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            return HostInfo(
                name=name,
                ip_address="127.0.0.1",
                status=self._determine_status(),
                role=role,
                uptime_seconds=uptime.total_seconds(),
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage("/").percent,
                temperature_celsius=self._get_temperature(),
                last_check=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error getting host info: {e}")
            return HostInfo(
                name=name,
                ip_address="127.0.0.1",
                status=HostStatus.ERROR,
                role=role,
                uptime_seconds=0,
                cpu_percent=0,
                memory_percent=0,
                disk_percent=0,
                last_check=datetime.now(),
            )

    def _determine_status(self) -> HostStatus:
        """Determine host status based on metrics"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        if cpu > 90 or memory > 90 or disk > 90:
            return HostStatus.ERROR
        elif cpu > 70 or memory > 70 or disk > 80:
            return HostStatus.WARNING
        return HostStatus.HEALTHY

    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        return entry.current
        except Exception:
            pass
        return None

    def get_process_info(self, pid: int) -> Optional[Dict]:
        """Get process information by PID"""
        try:
            proc = psutil.Process(pid)
            return {
                "pid": pid,
                "name": proc.name(),
                "status": proc.status(),
                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                "cpu_percent": proc.cpu_percent(),
                "num_threads": proc.num_threads(),
                "create_time": datetime.fromtimestamp(proc.create_time()),
            }
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return None


health_service = HealthService()
