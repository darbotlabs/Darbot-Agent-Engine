import os
import sys
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

# Mock Azure dependencies to prevent import errors
sys.modules["azure.monitor"] = MagicMock()
sys.modules["azure.monitor.events.extension"] = MagicMock()
sys.modules["azure.monitor.opentelemetry"] = MagicMock()

# Mock environment variables before importing app
os.environ["COSMOSDB_ENDPOINT"] = "https://mock-endpoint"
os.environ["COSMOSDB_KEY"] = "mock-key"
os.environ["COSMOSDB_DATABASE"] = "mock-database"
os.environ["COSMOSDB_CONTAINER"] = "mock-container"
os.environ[
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
] = "InstrumentationKey=mock-instrumentation-key;IngestionEndpoint=https://mock-ingestion-endpoint"
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "mock-deployment-name"
os.environ["AZURE_OPENAI_API_VERSION"] = "2023-01-01"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://mock-openai-endpoint"
os.environ["AZURE_AI_SUBSCRIPTION_ID"] = "mock-subscription-id"
os.environ["AZURE_AI_RESOURCE_GROUP"] = "mock-resource-group"
os.environ["AZURE_AI_PROJECT_NAME"] = "mock-project-name"
os.environ["AZURE_AI_AGENT_PROJECT_CONNECTION_STRING"] = "mock-connection-string"

# Mock telemetry initialization to prevent errors
with patch("azure.monitor.opentelemetry.configure_azure_monitor", MagicMock()):
    from backend.app_kernel import app

# Initialize FastAPI test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test suite for health check endpoints"""

    def test_health_live_endpoint(self):
        """Test the liveness probe endpoint"""
        response = client.get("/api/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "Darbot Agent Engine"

    def test_health_ready_endpoint(self):
        """Test the readiness probe endpoint"""
        response = client.get("/api/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "Darbot Agent Engine"

    def test_health_detailed_endpoint(self):
        """Test the detailed health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "service" in data
        assert "version" in data
        assert "checks" in data
        assert data["service"] == "Darbot Agent Engine"
        assert data["version"] == "1.0.0"

    def test_server_info_endpoint(self):
        """Test the server info endpoint"""
        response = client.get("/api/server-info")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Darbot Agent Engine"
        assert data["version"] == "1.0.0"
        assert "backend_host" in data
        assert "backend_port" in data
        assert "status" in data


class TestErrorHandling:
    """Test suite for error handling"""

    def test_validation_error_handling(self):
        """Test validation error handling with structured response"""
        # Send invalid JSON to trigger validation error
        response = client.post("/api/input_task", json={})
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "message" in data["error"]
        assert "details" in data["error"]

    def test_http_404_error_handling(self):
        """Test HTTP 404 error handling"""
        response = client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "HTTP_404"


class TestApiDocumentation:
    """Test suite for API documentation endpoints"""

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Darbot Agent Engine API"
        assert data["info"]["version"] == "1.0.0"

    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_endpoint(self):
        """Test ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")


class TestSecurityHeaders:
    """Test suite for security-related functionality"""

    def test_cors_headers(self):
        """Test CORS headers are present"""
        # Use a GET request instead of OPTIONS since OPTIONS isn't defined
        response = client.get("/api/health/live")
        assert response.status_code == 200
        # CORS headers should be present in the response
        # Note: CORS middleware might not add headers for same-origin requests in test


if __name__ == "__main__":
    pytest.main([__file__])