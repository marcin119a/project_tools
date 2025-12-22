from datetime import datetime, UTC
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from models.database import get_db
from schemas.health import HealthResponse, HealthStatus

router = APIRouter(prefix="/health")


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Check if the API and database are working properly",
)
async def health_check(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> HealthResponse:
    """
    Endpoint to verify the API and database are working properly.
    
    Returns:
    - status: "healthy" if everything is working, "unhealthy" otherwise
    - timestamp: timestamp of the check
    - database: status of the database connection
    """
    try:
        # Check the database connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        database_status = "connected"
        overall_status = HealthStatus.healthy
    except Exception as e:
        database_status = f"error: {str(e)}"
        overall_status = HealthStatus.unhealthy
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC),
        database=database_status,
    )

