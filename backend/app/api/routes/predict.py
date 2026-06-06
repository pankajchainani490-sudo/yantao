from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import run_prediction


router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        return PredictionResponse(**run_prediction(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
