"""
Tests for hello endpoint.
"""
import pytest
from httpx import AsyncClient

from schemas.hello import HelloResponse


@pytest.mark.asyncio
async def test_hello_world(test_client_no_db: AsyncClient):
    """Test hello world endpoint without name parameter."""
    response = await test_client_no_db.get("/hello")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "message" in data
    
    # Check value
    assert data["message"] == "Hello World"


@pytest.mark.asyncio
async def test_hello_world_response_model(test_client_no_db: AsyncClient):
    """Test that hello world response matches Pydantic model."""
    response = await test_client_no_db.get("/hello")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response can be parsed as HelloResponse
    hello_response = HelloResponse(**data)
    
    assert hello_response.message == "Hello World"
    assert isinstance(hello_response.message, str)


@pytest.mark.asyncio
async def test_hello_world_content_type(test_client_no_db: AsyncClient):
    """Test that hello world response has correct content type."""
    response = await test_client_no_db.get("/hello")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_hello_with_name(test_client_no_db: AsyncClient):
    """Test hello endpoint with name parameter."""
    response = await test_client_no_db.get("/hello/John")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Check response structure
    assert "message" in data
    
    # Check value
    assert data["message"] == "Hello John"


@pytest.mark.asyncio
async def test_hello_with_different_names(test_client_no_db: AsyncClient):
    """Test hello endpoint with different name parameters."""
    names = ["Alice", "Bob", "Charlie", "Дмитрий", "李明"]
    
    for name in names:
        response = await test_client_no_db.get(f"/hello/{name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Hello {name}"


@pytest.mark.asyncio
async def test_hello_with_name_response_model(test_client_no_db: AsyncClient):
    """Test that hello with name response matches Pydantic model."""
    response = await test_client_no_db.get("/hello/Jane")
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response can be parsed as HelloResponse
    hello_response = HelloResponse(**data)
    
    assert hello_response.message == "Hello Jane"
    assert isinstance(hello_response.message, str)


@pytest.mark.asyncio
async def test_hello_with_special_characters(test_client_no_db: AsyncClient):
    """Test hello endpoint with special characters in name."""
    # Test with URL-safe special characters
    response = await test_client_no_db.get("/hello/John%20Doe")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello John Doe"

