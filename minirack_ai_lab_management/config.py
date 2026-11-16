"""Configuration management"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # App settings
    DEBUG: bool = Field(default=False, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8080, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Security
    API_KEY_SECRET: str = Field(default="change-me-in-production", description="API secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="JWT expiration hours")
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )

    # LaForge host configuration (ai-utility)
    LAFORGE_HOST: str = Field(default="192.168.1.161", description="LaForge (ai-utility) host")
    LAFORGE_SSH_USER: str = Field(default="localadmin", description="SSH user")
    LAFORGE_SSH_PORT: int = Field(default=22, description="SSH port")

    # Data host configuration (ai-core)
    DATA_HOST: str = Field(default="192.168.1.160", description="Data (ai-core) host")
    OLLAMA_API_HOST: str = Field(default="http://192.168.1.160:11434", description="Ollama API URL")

    # Web host configuration (ai-web/RIKER)
    RIKER_HOST: str = Field(default="192.168.1.162", description="Riker (ai-web) host")
    OPENWEB_UI_URL: str = Field(default="http://192.168.1.162:8000", description="Open WebUI URL")

    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")
    METRICS_RETENTION_HOURS: int = Field(default=24, description="Metrics retention period")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
