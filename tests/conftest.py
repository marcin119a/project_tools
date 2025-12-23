"""
Pytest configuration and fixtures for the project.

This module provides shared test fixtures for:
- Test database setup and teardown
- FastAPI test client
- Database session management
"""
import pytest
import asyncio
from typing import AsyncGenerator
from pathlib import Path
import tempfile
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from models.base import Base
from models.database import get_db
from main import app


# Test database URL - using in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """
    Create a test database engine with in-memory SQLite.
    Each test function gets a fresh database.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL query debugging
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Each test gets a fresh session that is rolled back after the test.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def test_session_with_commit(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session that commits changes.
    Use this when you need to test committed transactions.
    """
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.commit()


@pytest.fixture(scope="function")
def override_get_db(test_session):
    """
    Override the get_db dependency to use the test session.
    This allows tests to use the FastAPI dependency injection system.
    """
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session
    
    return _get_test_db


@pytest.fixture(scope="function")
async def test_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a FastAPI test client with overridden database dependency.
    Use this for testing API endpoints.
    """
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Cleanup: remove dependency override after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_client_no_db() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a FastAPI test client without database dependency override.
    Use this for testing endpoints that don't require database access.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def sync_test_client(override_get_db) -> TestClient:
    """
    Create a synchronous FastAPI TestClient with overridden database dependency.
    Use this for testing API endpoints with FastAPI's TestClient.
    
    Note: TestClient is synchronous but works with async endpoints.
    The fixture is async to ensure the test_session is properly set up.
    """
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Cleanup: remove dependency override after test
    app.dependency_overrides.clear()

