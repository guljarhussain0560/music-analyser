from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Asserts that root endpoint returns operational metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert data["docs"] == "/docs"


def test_health_endpoint(client: TestClient):
    """Asserts that /health endpoint returns 200 OK with connected database."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_api_health_endpoint(client: TestClient):
    """Asserts that /api/health endpoint returns identical health schema."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
