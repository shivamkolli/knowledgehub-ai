from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app


def test_health_returns_service_status() -> None:
    application = create_app()
    application.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None, app_name="Test KnowledgeHub", environment="test"
    )

    with TestClient(application) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Test KnowledgeHub"}
