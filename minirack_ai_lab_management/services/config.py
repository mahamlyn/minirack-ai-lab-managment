"""Configuration management service"""
import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigService:
    """Service for managing MiniRack configuration"""

    def __init__(self):
        self.config_dir = Path("/etc/minirack-ai-lab")
        self.config_file = self.config_dir / "config.yaml"
        self.config_cache: Optional[Dict[str, Any]] = None
        self.last_load: Optional[datetime] = None

    async def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config = yaml.safe_load(f)
                    self.config_cache = config
                    self.last_load = datetime.now()
                    return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")

        return self.config_cache or {}

    async def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update a configuration value"""
        try:
            config = await self.load_config()
            if section not in config:
                config[section] = {}

            config[section][key] = value

            if self.config_file.parent.exists():
                with open(self.config_file, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
                self.config_cache = config
                logger.info(f"Updated config: {section}.{key} = {value}")
                return True
        except Exception as e:
            logger.error(f"Error updating config: {e}")

        return False

    async def get_ollama_model(self) -> str:
        """Get configured Ollama model"""
        config = await self.load_config()
        return config.get("ollama_model", "llama3.2")

    async def get_ollama_host(self) -> str:
        """Get configured Ollama host binding"""
        config = await self.load_config()
        return config.get("ollama_host", "0.0.0.0:11434")

    async def get_docker_config(self) -> Dict[str, Any]:
        """Get Docker configuration"""
        config = await self.load_config()
        return config.get("docker", {})

    async def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration"""
        try:
            config = await self.load_config()
            issues = []

            # Check required fields
            if not config.get("ollama_model"):
                issues.append("Missing ollama_model")
            if not config.get("ollama_host"):
                issues.append("Missing ollama_host")

            return {"valid": len(issues) == 0, "issues": issues, "config": config}
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return {"valid": False, "issues": [str(e)], "config": {}}

    async def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information"""
        try:
            config = await self.load_config()
            return {
                "environment": config.get("environment", "production"),
                "version": config.get("version", "1.0.0"),
                "deployed_at": config.get("deployed_at", "unknown"),
                "hosts": {
                    "ai_core": config.get("ai_core_host", "192.168.1.160"),
                    "ai_web": config.get("ai_web_host", "192.168.1.162"),
                    "ai_utility": config.get("ai_utility_host", "192.168.1.161"),
                },
            }
        except Exception as e:
            logger.error(f"Error getting deployment info: {e}")
            return {}


config_service = ConfigService()
