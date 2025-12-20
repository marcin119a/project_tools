from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Status zdrowia serwisu"""
    healthy = "healthy"
    unhealthy = "unhealthy"


class HealthResponse(BaseModel):
    """Odpowiedź z endpointu health check"""
    status: HealthStatus = Field(..., description="Ogólny status serwisu")
    timestamp: datetime = Field(..., description="Czas sprawdzenia")
    database: str = Field(..., description="Status połączenia z bazą danych")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00",
                "database": "connected",
            }
        }

