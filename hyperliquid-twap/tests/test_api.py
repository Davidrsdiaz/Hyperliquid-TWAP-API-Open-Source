"""Tests for API endpoints."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns basic info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_get_twaps_missing_params():
    """Test that missing required params returns 422."""
    response = client.get("/api/v1/twaps")
    assert response.status_code == 422


def test_get_twaps_with_params():
    """Test GET /api/v1/twaps with valid parameters."""
    response = client.get(
        "/api/v1/twaps",
        params={
            "wallet": "0xabc123",
            "start": "2025-11-01T00:00:00Z",
            "end": "2025-11-04T00:00:00Z"
        }
    )
    
    # Should return 200 even with no data
    assert response.status_code == 200
    data = response.json()
    
    assert "wallet" in data
    assert "start" in data
    assert "end" in data
    assert "twaps" in data
    assert isinstance(data["twaps"], list)


def test_get_twap_by_id_not_found():
    """Test GET /api/v1/twaps/{twap_id} for non-existent TWAP."""
    response = client.get("/api/v1/twaps/nonexistent123")
    assert response.status_code == 404


def test_api_docs_available():
    """Test that API docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
