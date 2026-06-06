from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.monitor import LocalPortTargetRequest, SiteTargetRequest, TrafficObservationRequest
from app.services import monitor_service


router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/target")
def get_target(target_id: Optional[int] = None) -> dict:
    try:
        return monitor_service.get_site_target(target_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/targets")
def targets() -> dict:
    return {"items": monitor_service.list_site_targets()}


@router.post("/targets/localhost")
def add_localhost_target(request: LocalPortTargetRequest) -> dict:
    try:
        return monitor_service.add_localhost_target(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/target")
def update_target(request: SiteTargetRequest) -> dict:
    try:
        return monitor_service.set_site_target(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/ingest")
def ingest_observation(request: TrafficObservationRequest) -> dict:
    try:
        return monitor_service.ingest_observation(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/events")
def events(
    limit: int = Query(default=50, ge=1, le=200),
    target_id: Optional[int] = None,
    target_host: Optional[str] = None,
) -> dict:
    return {
        "items": monitor_service.list_monitor_events(
            limit=limit,
            target_id=target_id,
            target_host=target_host,
        )
    }


@router.get("/summary")
def summary(target_id: Optional[int] = None) -> dict:
    try:
        return monitor_service.get_monitor_summary(target_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
