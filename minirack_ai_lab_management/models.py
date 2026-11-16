"""Data models and schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class HostStatus(str, Enum):
    """Host status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


class HostInfo(BaseModel):
    """Host information model"""
    name: str
    ip_address: str
    status: HostStatus
    role: str  # ai-core, ai-web, ai-utility
    uptime_seconds: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    temperature_celsius: Optional[float] = None
    last_check: datetime


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceInfo(BaseModel):
    """Service information model"""
    name: str
    host: str
    status: ServiceStatus
    process_id: Optional[int] = None
    memory_mb: float
    cpu_percent: float
    uptime_seconds: float
    last_check: datetime


class OllamaModelInfo(BaseModel):
    """Ollama model information"""
    name: str
    size_gb: float
    quantization: str
    parameters: str
    last_used: datetime
    usage_count: int


class SystemMetrics(BaseModel):
    """System metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io_bytes: float
    network_errors: int


class DashboardData(BaseModel):
    """Dashboard data aggregation"""
    hosts: List[HostInfo]
    services: List[ServiceInfo]
    models: List[OllamaModelInfo]
    recent_metrics: List[SystemMetrics]
    alerts: List[str]


class ConfigUpdate(BaseModel):
    """Configuration update request"""
    service: str
    setting: str
    value: Any
    reason: Optional[str] = None


class LogEntry(BaseModel):
    """Log entry"""
    timestamp: datetime
    level: str
    service: str
    message: str
    details: Optional[Dict[str, Any]] = None
