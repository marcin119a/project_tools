from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class OfferResponse(BaseModel):
    """Response model for a single offer/listing."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "listing_id": 1,
                "price_total_zl": "500000.00",
                "price_sqm_zl": "10000.00",
                "area": "50.00",
                "rooms": 3,
                "date_posted": "2024-01-15",
            }
        }
    )
    
    listing_id: Optional[int] = Field(None, description="Unique identifier for the listing")
    price_total_zl: Optional[Decimal] = Field(None, description="Total price in PLN")
    price_sqm_zl: Optional[Decimal] = Field(None, description="Price per square meter in PLN")
    area: Optional[Decimal] = Field(None, description="Area in square meters")
    rooms: Optional[int] = Field(None, description="Number of rooms")
    date_posted: Optional[date] = Field(None, description="Date when the listing was posted")


class OffersListResponse(BaseModel):
    """Response model for a list of offers."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "offers": [
                    {
                        "listing_id": 1,
                        "price_total_zl": "500000.00",
                        "price_sqm_zl": "10000.00",
                        "area": "50.00",
                        "rooms": 3,
                        "date_posted": "2024-01-15",
                    }
                ],
                "total": 1
            }
        }
    )
    
    offers: List[OfferResponse] = Field(..., description="List of offers")
    total: int = Field(..., description="Total number of offers")

