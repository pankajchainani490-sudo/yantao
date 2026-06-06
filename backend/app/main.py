from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.router import api_router
from app.core.config import settings
from app.db.database import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Machine-learning-based malicious traffic detection backend.",
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Malicious Traffic ML Detection System backend is running.",
        "docs": "/docs",
    }
