from fastapi import APIRouter

from app.core.config import settings
from app.services.prediction_service import get_supported_models


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def get_settings() -> dict:
    return {
        "default_model_name": settings.default_model_name,
        "supported_models": get_supported_models(),
        "auto_blacklist_threshold": settings.auto_blacklist_threshold,
        "demo_mode": True,
    }
