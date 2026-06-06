from fastapi import APIRouter

from app.services.metrics_service import get_metrics_summary


router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary")
def metrics_summary() -> dict:
    return get_metrics_summary()
