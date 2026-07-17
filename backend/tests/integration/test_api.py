import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
def test_health_check(client: TestClient):
    """Verify that the health check endpoint returns 200 OK and system metrics."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"
    assert len(data["data"]["checks"]) == 3  # DB, Provider, System

@pytest.mark.integration
def test_readiness_probe(client: TestClient):
    """Verify kubernetes readiness probe."""
    response = client.get("/ready")
    assert response.status_code == 200

@pytest.mark.integration
def test_liveness_probe(client: TestClient):
    """Verify kubernetes liveness probe."""
    response = client.get("/live")
    assert response.status_code == 200

@pytest.mark.integration
def test_prometheus_metrics(client: TestClient):
    """Verify that the prometheus middleware tracks and exposes metrics."""
    # Hit an endpoint to generate data
    client.get("/ready")
    
    # Check metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    metrics_text = response.text
    
    assert "http_requests_total" in metrics_text
    assert "http_request_duration_seconds" in metrics_text
    assert "method=\"GET\"" in metrics_text
    assert "endpoint=\"/ready\"" in metrics_text

@pytest.mark.integration
def test_unauthorized_access(client: TestClient):
    """Verify that endpoints requiring authentication reject unauthenticated requests."""
    response = client.get("/api/v1/leads")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert "Not authenticated" in response.json()["error"]["message"]

@pytest.mark.integration
def test_validation_error_formatting(client: TestClient):
    """Verify that pydantic validation errors are formatted correctly."""
    # Payload is missing required fields (e.g. password)
    response = client.post("/api/v1/auth/register", json={"email": "bad_email"})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "UNPROCESSABLE_ENTITY"
    assert "details" in data["error"]
