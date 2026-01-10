from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from models.database import get_db
from models.models import Listing
from schemas.offers import OfferResponse, OffersListResponse
from utils.sorter import OfferSorter


router = APIRouter()


def _convert_sort_params(sort_by: str, order: str) -> str:
    """
    Convert sort_by and order parameters to OfferSorter format.
    
    Args:
        sort_by: Field to sort by (e.g., "price", "area", "date")
        order: Sort order ("asc" or "desc")
    
    Returns:
        Sort option string for OfferSorter (e.g., "price_desc", "area_asc")
    
    Raises:
        ValueError: If sort_by or order is invalid
    """
    valid_sort_fields = {"price", "price_per_sqm", "date", "area"}
    valid_orders = {"asc", "desc"}
    
    if sort_by not in valid_sort_fields:
        raise ValueError(f"Invalid sort_by field: {sort_by}. Valid fields: {valid_sort_fields}")
    
    if order not in valid_orders:
        raise ValueError(f"Invalid order: {order}. Valid orders: {valid_orders}")
    
    # Map sort_by to OfferSorter format
    sort_mapping = {
        "price": "price",
        "price_per_sqm": "price_per_sqm",
        "date": "date_newest",  # date always sorts newest first
        "area": "area",
    }
    
    # Special handling for date (always newest first)
    if sort_by == "date":
        return "date_newest"
    
    # For other fields, combine sort_by and order
    return f"{sort_mapping[sort_by]}_{order}"


@router.get(
    "/offers",
    response_model=OffersListResponse,
    summary="Get offers/listings",
    description="Get a list of offers/listings with optional sorting",
)
async def get_offers(
    sort_by: str = Query(default="najtrafniejsze", description="Field to sort by (price, price_per_sqm, date, area)"),
    order: str = Query(default="asc", description="Sort order (asc or desc)"),
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
) -> OffersListResponse:
    """
    Get offers/listings with optional sorting.
    
    Args:
        sort_by: Field to sort by. Options: "price", "price_per_sqm", "date", "area", or "najtrafniejsze" (default)
        order: Sort order. Options: "asc" (ascending) or "desc" (descending). Default: "asc"
        db: Database session dependency
    
    Returns:
        OffersListResponse: List of offers with total count
    """
    # Query all listings from database
    result = await db.execute(select(Listing))
    listings = result.scalars().all()
    
    # Convert SQLModel instances to dictionaries for OfferSorter
    offers_dict = []
    for listing in listings:
        offer_dict = {
            "listing_id": listing.listing_id,
            "price_total_zl": listing.price_total_zl,
            "price_sqm_zl": listing.price_sqm_zl,
            "area": listing.area,
            "rooms": listing.rooms,
            "date_posted": listing.date_posted,
        }
        offers_dict.append(offer_dict)
    
    # Handle default sorting (najtrafniejsze)
    if sort_by == "najtrafniejsze":
        sort_option = None
    else:
        # Convert sort_by and order to OfferSorter format
        sort_option = _convert_sort_params(sort_by, order)
    
    # Sort offers using OfferSorter
    sorter = OfferSorter()
    sorted_offers = sorter.sort(offers_dict, sort_by=sort_option)
    
    # Convert dictionaries to Pydantic models
    offer_responses = [OfferResponse(**offer) for offer in sorted_offers]
    
    return OffersListResponse(
        offers=offer_responses,
        total=len(offer_responses)
    )

