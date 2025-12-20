from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from models.database import get_db
from schemas.health import HealthResponse, HealthStatus

router = APIRouter(prefix="/health",)


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Sprawdza czy API i baza danych działają poprawnie",
)
async def health_check(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> HealthResponse:
    """
    Endpoint do weryfikacji działania API i połączenia z bazą danych.
    
    Zwraca:
    - status: "healthy" jeśli wszystko działa, "unhealthy" w przeciwnym razie
    - timestamp: czas sprawdzenia
    - database: status połączenia z bazą danych
    """
    try:
        # Sprawdzenie połączenia z bazą danych
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        database_status = "connected"
        overall_status = HealthStatus.healthy
    except Exception as e:
        database_status = f"error: {str(e)}"
        overall_status = HealthStatus.unhealthy
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        database=database_status,
    )

