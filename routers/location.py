from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import get_db
from models.models import Location
from schemas.location import LocationCreate, LocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get(
    "/",
    response_model=List[LocationResponse],
    summary="Lista wszystkich lokalizacji",
    description="Zwraca listę wszystkich lokalizacji w systemie",
)
async def get_locations(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[LocationResponse]:
    """
    Pobiera wszystkie lokalizacje z bazy danych.
    
    Args:
        db: Sesja bazy danych (dependency injection)
    
    Returns:
        List[LocationResponse]: Lista wszystkich lokalizacji
    """
    try:
        result = await db.execute(select(Location))
        locations = result.scalars().all()
        return [LocationResponse.model_validate(loc) for loc in locations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas pobierania lokalizacji: {str(e)}",
        )


@router.post(
    "/",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Utworzenie nowej lokalizacji",
    description="Dodaje nową lokalizację do systemu. Wszystkie pola są opcjonalne.",
)
async def create_location(
    location_data: LocationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationResponse:
    """
    Tworzy nową lokalizację w bazie danych.
    
    Args:
        location_data: Dane lokalizacji do utworzenia (wszystkie pola opcjonalne)
        db: Sesja bazy danych (dependency injection)
    
    Returns:
        LocationResponse: Utworzona lokalizacja z przypisanym location_id
    
    Raises:
        HTTPException: W przypadku błędu podczas zapisu do bazy danych
    """
    try:
        # Tworzenie nowego obiektu Location z danymi z requestu
        new_location = Location(**location_data.model_dump(exclude_unset=False))
        
        # Dodanie do sesji i zapisanie
        db.add(new_location)
        await db.commit()
        await db.refresh(new_location)
        
        # Zwrócenie utworzonej lokalizacji
        return LocationResponse.model_validate(new_location)
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas tworzenia lokalizacji: {str(e)}",
        )

