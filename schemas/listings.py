from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class ListingFilterParams(BaseModel):
    """Parameters for filtering listings"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price_min": 500000,
                "price_max": 1000000,
                "price_sqm_min": 10000,
                "price_sqm_max": 20000,
                "rooms": [2, 3],
                "city": "Warszawa",
                "city_district": "Białołęka",
            }
        }
    )
    
    price_min: Optional[Decimal] = Field(
        None,
        description="Minimum total price in PLN",
        ge=0,
    )
    price_max: Optional[Decimal] = Field(
        None,
        description="Maximum total price in PLN",
        ge=0,
    )
    price_sqm_min: Optional[Decimal] = Field(
        None,
        description="Minimum price per square meter in PLN",
        ge=0,
    )
    price_sqm_max: Optional[Decimal] = Field(
        None,
        description="Maximum price per square meter in PLN",
        ge=0,
    )
    rooms: Optional[List[int]] = Field(
        None,
        description="List of room counts to filter (e.g., [2, 3] for 2 and 3 room apartments)",
    )
    city: Optional[str] = Field(
        None,
        description="City name for filtering",
        max_length=255,
    )
    city_district: Optional[str] = Field(
        None,
        description="City district name for filtering",
        max_length=255,
    )


class LocationResponse(BaseModel):
    """Location information in listing response"""
    location_id: int
    city: Optional[str] = None
    locality: Optional[str] = None
    city_district: Optional[str] = None
    street: Optional[str] = None
    full_address: Optional[str] = None


class ListingResponse(BaseModel):
    """Listing information in response"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "listing_id": 1,
                "rooms": 3,
                "area": 65.5,
                "price_total_zl": 860000,
                "price_sqm_zl": 13130,
                "location": {
                    "location_id": 1,
                    "city": "Warszawa",
                    "city_district": "Białołęka",
                    "locality": None,
                    "street": "ul. Józefa Mehoffera",
                    "full_address": "Warszawa Białołęka, ul. Józefa Mehoffera",
                },
            }
        }
    )
    
    listing_id: int
    rooms: Optional[int] = None
    area: Optional[Decimal] = None
    price_total_zl: Optional[Decimal] = None
    price_sqm_zl: Optional[Decimal] = None
    location: LocationResponse


class ListingFilterResponse(BaseModel):
    """Response for filtered listings with count"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "count": 124,
                "listings": [
                    {
                        "listing_id": 1,
                        "rooms": 3,
                        "area": 65.5,
                        "price_total_zl": 860000,
                        "price_sqm_zl": 13130,
                        "location": {
                            "location_id": 1,
                            "city": "Warszawa",
                            "city_district": "Białołęka",
                        },
                    }
                ],
            }
        }
    )
    
    count: int = Field(..., description="Total number of listings matching the filters")
    listings: List[ListingResponse] = Field(..., description="List of filtered listings")


class LocationAutocompleteItem(BaseModel):
    """Single location item for autocomplete"""
    location_id: int
    city: Optional[str] = None
    city_district: Optional[str] = None
    locality: Optional[str] = None
    display_name: str = Field(..., description="Formatted display name for the location")


class LocationAutocompleteResponse(BaseModel):
    """Response for location autocomplete"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "locations": [
                    {
                        "location_id": 1,
                        "city": "Warszawa",
                        "city_district": "Białołęka",
                        "locality": None,
                        "display_name": "Warszawa, Białołęka",
                    }
                ],
            }
        }
    )
    
    locations: List[LocationAutocompleteItem] = Field(
        ...,
        description="List of matching locations for autocomplete",
    )

