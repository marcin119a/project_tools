from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    """Schema dla tworzenia nowej lokalizacji - wszystkie pola opcjonalne"""
    
    city: Optional[str] = Field(None, description="Nazwa miasta", max_length=255)
    locality: Optional[str] = Field(None, description="Miejscowość", max_length=255)
    city_district: Optional[str] = Field(None, description="Dzielnica miasta", max_length=255)
    street: Optional[str] = Field(None, description="Ulica", max_length=255)
    full_address: Optional[str] = Field(None, description="Pełny adres", max_length=500)
    latitude: Optional[Decimal] = Field(None, description="Szerokość geograficzna")
    longitude: Optional[Decimal] = Field(None, description="Długość geograficzna")

    class Config:
        json_schema_extra = {
            "example": {
                "city": "Warszawa",
                "locality": "Śródmieście",
                "city_district": "Mokotów",
                "street": "ul. Marszałkowska 1",
                "full_address": "Marszałkowska 1, 00-001 Warszawa",
                "latitude": "52.229676",
                "longitude": "21.012229",
            }
        }


class LocationResponse(BaseModel):
    """Schema dla odpowiedzi z danymi lokalizacji"""
    
    location_id: int = Field(..., description="Unikalny identyfikator lokalizacji")
    city: Optional[str] = Field(None, description="Nazwa miasta")
    locality: Optional[str] = Field(None, description="Miejscowość")
    city_district: Optional[str] = Field(None, description="Dzielnica miasta")
    street: Optional[str] = Field(None, description="Ulica")
    full_address: Optional[str] = Field(None, description="Pełny adres")
    latitude: Optional[Decimal] = Field(None, description="Szerokość geograficzna")
    longitude: Optional[Decimal] = Field(None, description="Długość geograficzna")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "location_id": 1,
                "city": "Warszawa",
                "locality": "Śródmieście",
                "city_district": "Mokotów",
                "street": "ul. Marszałkowska 1",
                "full_address": "Marszałkowska 1, 00-001 Warszawa",
                "latitude": "52.229676",
                "longitude": "21.012229",
            }
        }

