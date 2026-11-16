"""Configuration endpoints"""
from fastapi import APIRouter, HTTPException
from minirack_ai_lab_management.services.config import config_service
from minirack_ai_lab_management.models import ConfigUpdate
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    return await config_service.load_config()


@router.get("/deployment")
async def get_deployment_info() -> Dict[str, Any]:
    """Get deployment information"""
    return await config_service.get_deployment_info()


@router.post("/update")
async def update_config(update: ConfigUpdate) -> Dict[str, Any]:
    """Update configuration setting"""
    success = await config_service.update_config(update.service, update.setting, update.value)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update configuration")
    return {"success": True, "message": f"Updated {update.service}.{update.setting}"}


@router.post("/validate")
async def validate_config() -> Dict[str, Any]:
    """Validate current configuration"""
    return await config_service.validate_config()


@router.get("/ollama")
async def get_ollama_config() -> Dict[str, Any]:
    """Get Ollama configuration"""
    return {
        "model": await config_service.get_ollama_model(),
        "host": await config_service.get_ollama_host(),
    }


@router.post("/ollama/model")
async def set_ollama_model(model: str) -> Dict[str, Any]:
    """Set Ollama model"""
    success = await config_service.update_config("ollama", "model", model)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update Ollama model")
    return {"success": True, "model": model}
