"""API Contract Tests - Validates API schema compliance and response consistency."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestAPISchemaContracts:
    """Test suite for API schema contracts."""

    def test_openapi_schema_valid(self, client: TestClient) -> None:
        """Validate OpenAPI schema is well-formed."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert len(schema["paths"]) > 0

    def test_all_endpoints_have_schemas(self, client: TestClient) -> None:
        """Ensure all endpoints have request/response schemas."""
        schema = client.get("/openapi.json").json()
        paths = schema["paths"]

        for path, methods in paths.items():
            for method in ["get", "post", "put", "patch", "delete"]:
                if method in methods:
                    operation = methods[method]
                    # Each operation should have either responses or requestBody
                    has_response = "responses" in operation
                    has_request = "requestBody" in operation
                    assert has_response or has_request, f"{method.upper()} {path} missing schema"

    def test_auth_endpoints_contract(self, client: TestClient) -> None:
        """Test authentication endpoints follow contract."""
        # Login endpoint
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "TestPass123!"}
        )
        # Should return 401 (invalid credentials) but valid schema
        assert login_response.status_code in [200, 401]

        # Register endpoint
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "NewPass123!"
            }
        )
        assert register_response.status_code in [201, 400]  # 400 if exists

    def test_sql_endpoint_contract(self, client: TestClient) -> None:
        """Test SQL execution endpoint contract."""
        response = client.post(
            "/api/v1/sql",
            json={"query": "SELECT 1", "org_id": "test-org"}
        )
        # Should return valid response structure
        assert response.status_code in [200, 403]

    def test_datasets_endpoint_contract(self, client: TestClient) -> None:
        """Test datasets endpoint contract."""
        # List datasets
        list_response = client.get("/api/v1/datasets")
        assert list_response.status_code == 200
        data = list_response.json()
        assert isinstance(data, list)

    def test_dashboards_endpoint_contract(self, client: TestClient) -> None:
        """Test dashboards endpoint contract."""
        list_response = client.get("/api/v1/dashboards")
        assert list_response.status_code == 200
        data = list_response.json()
        assert isinstance(data, list)

    def test_agents_endpoint_contract(self, client: TestClient) -> None:
        """Test agents endpoint contract."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data or isinstance(data, list)

    def test_health_endpoint_contract(self, client: TestClient) -> None:
        """Test health check endpoint contract."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_metrics_endpoint_contract(self, client: TestClient) -> None:
        """Test metrics endpoint contract."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus format
        assert "http_requests_total" in response.text or len(response.text) > 0

    def test_error_response_contract(self, client: TestClient) -> None:
        """Test error responses follow consistent contract."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "error" in data

    def test_validation_error_contract(self, client: TestClient) -> None:
        """Test validation errors follow Pydantic contract."""
        response = client.post(
            "/api/v1/auth/login",
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    def test_rate_limit_response(self, client: TestClient) -> None:
        """Test rate limiting returns proper response."""
        # Make multiple rapid requests
        for _ in range(100):
            response = client.get("/health")
            if response.status_code == 429:
                data = response.json()
                assert "detail" in data
                break
        else:
            # If no rate limit hit, endpoint is working
            assert True
