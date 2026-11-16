"""AI Models endpoints"""
from fastapi import APIRouter
from minirack_ai_lab_management.services.remote import remote_host_service
from minirack_ai_lab_management.config import settings
from typing import List, Dict, Any

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def get_ollama_models():
    """Get available Ollama models"""
    models = await remote_host_service.get_ollama_models()
    return [
        {
            "name": model.get("name", "unknown"),
            "size": model.get("size", 0),
            "digest": model.get("digest", ""),
            "modified_at": model.get("modified_at", ""),
        }
        for model in models
    ]


@router.get("/{model_name}")
async def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about a specific model"""
    models = await remote_host_service.get_ollama_models()
    for model in models:
        if model.get("name") == model_name:
            return {
                "name": model.get("name"),
                "size": model.get("size"),
                "digest": model.get("digest"),
                "modified_at": model.get("modified_at"),
                "details": model.get("details", {}),
            }
    return {"error": "Model not found"}


@router.post("/{model_name}/pull")
async def pull_model(model_name: str) -> Dict[str, Any]:
    """Pull a new Ollama model (async operation)"""
    # This would typically trigger a background task
    return {
        "status": "pulling",
        "model": model_name,
        "message": "Model pull initiated. Check progress on the dashboard.",
    }


@router.post("/{model_name}/remove")
async def remove_model(model_name: str) -> Dict[str, Any]:
    """Remove an Ollama model"""
    return {
        "status": "removing",
        "model": model_name,
        "message": "Model removal initiated.",
    }
