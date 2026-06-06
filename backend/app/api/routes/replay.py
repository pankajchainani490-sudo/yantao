from fastapi import APIRouter

from app.repositories import security_repository
from app.schemas.blacklist import ReplayStartRequest


router = APIRouter(prefix="/replay", tags=["replay"])


@router.post("/start")
def start_replay(request: ReplayStartRequest) -> dict:
    return security_repository.start_replay(stage_order=request.stage_order)


@router.get("/status")
def replay_status() -> dict:
    return security_repository.get_replay_status()
