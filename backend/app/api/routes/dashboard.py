from fastapi import APIRouter

from app.repositories import security_repository


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary() -> dict:
    return security_repository.get_dashboard_summary()


@router.get("/trends")
def dashboard_trends() -> dict:
    return {"items": security_repository.get_dashboard_trends()}


@router.get("/top-sources")
def dashboard_top_sources() -> dict:
    return {"items": security_repository.get_dashboard_top_sources()}
