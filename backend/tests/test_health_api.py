from fastapi.testclient import TestClient

from app.main import app


def test_root_returns_docs_link() -> None:
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {
            "message": "Malicious Traffic ML Detection System backend is running.",
            "docs": "/docs",
        }


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "backend",
            "version": "0.1.0",
        }
