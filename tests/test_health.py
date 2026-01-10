"""
Tests for health check endpoint.
"""
import pytest
from datetime import datetime, UTC
from typing import AsyncGenerator
from httpx import AsyncClient
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.health import HealthStatus
from models.database import get_db
from main import app


@pytest.mark.asyncio
async def test_health_check_success(test_client: AsyncClient):
    """Test successful health check when database is connected."""
    response = await test_client.get("/health/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data
    
    # Check values
    assert data["status"] == HealthStatus.healthy
    assert data["database"] == "connected"
    
    # Verify timestamp is valid ISO format
    timestamp_str = data["timestamp"].replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(timestamp_str)
    assert isinstance(timestamp, datetime)
    
    # Verify timestamp is recent (within last 5 seconds)
    now = datetime.now(UTC)
    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 5


@pytest.mark.asyncio
async def test_health_check_response_model(test_client: AsyncClient):
    """Test that health check response matches Pydantic model."""
    response = await test_client.get("/health/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response can be parsed as HealthResponse
    from schemas.health import HealthResponse
    health_response = HealthResponse(**data)
    
    assert health_response.status == HealthStatus.healthy
    assert health_response.database == "connected"
    assert isinstance(health_response.timestamp, datetime)


@pytest.mark.asyncio
async def test_health_check_endpoint_path(test_client: AsyncClient):
    """Test health check endpoint is accessible at correct path."""
    # Test with trailing slash
    response = await test_client.get("/health/")
    assert response.status_code == 200
    
    # Test without trailing slash (FastAPI should redirect)
    response_no_slash = await test_client.get("/health")
    # FastAPI may redirect or return 200, both are acceptable
    assert response_no_slash.status_code in [200, 307, 308]


@pytest.fixture
def override_get_db_with_error():
    """Override get_db dependency to simulate database error."""
    async def _get_test_db_with_error() -> AsyncGenerator[AsyncSession, None]:
        # Create a mock session that raises error on execute
        mock_session = AsyncMock(spec=AsyncSession)
        
        async def failing_execute(*args, **kwargs):
            raise Exception("Database connection failed")
        
        mock_session.execute = failing_execute
        yield mock_session
    
    return _get_test_db_with_error


@pytest.mark.asyncio
async def test_health_check_database_error(override_get_db_with_error):
    """Test health check when database connection fails."""
    from httpx import ASGITransport
    
    app.dependency_overrides[get_db] = override_get_db_with_error
    
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/")
            
            assert response.status_code == 200
            
            data = response.json()
            
            # Check that status is unhealthy
            assert data["status"] == HealthStatus.unhealthy
            assert "error" in data["database"].lower()
            assert "timestamp" in data
    finally:
        # Cleanup
        app.dependency_overrides.clear()

