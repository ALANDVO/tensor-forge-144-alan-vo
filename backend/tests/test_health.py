"""Tests for health check endpoint."""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint returns healthy status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "tensor-forge-backend"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns service info."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tensor Forge 144"
        assert data["version"] == "1.0.0"
        assert "docs" in data