from fastapi import APIRouter, Query

from app.repositories import security_repository


router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def alerts(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    return {"items": security_repository.list_alerts(limit=limit)}
