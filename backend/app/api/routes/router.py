from fastapi import APIRouter

from app.api.routes.alerts import router as alerts_router
from app.api.routes.blacklist import router as blacklist_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.monitor import router as monitor_router
from app.api.routes.predict import router as predict_router
from app.api.routes.replay import router as replay_router
from app.api.routes.settings import router as settings_router
from app.api.routes.simulator import router as simulator_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(predict_router)
api_router.include_router(dashboard_router)
api_router.include_router(alerts_router)
api_router.include_router(blacklist_router)
api_router.include_router(replay_router)
api_router.include_router(metrics_router)
api_router.include_router(settings_router)
api_router.include_router(monitor_router)
api_router.include_router(simulator_router)
