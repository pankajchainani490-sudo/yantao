from fastapi import APIRouter, HTTPException

from app.schemas.monitor import SimulationRunRequest
from app.services.simulator_service import list_scenarios, run_simulation


router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.get("/scenarios")
def scenarios() -> dict:
    return {"items": list_scenarios()}


@router.post("/run")
def run(request: SimulationRunRequest) -> dict:
    try:
        return run_simulation(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
