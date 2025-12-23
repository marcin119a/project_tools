import json
from typing import Annotated, Optional, List
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from models.database import get_db
from models.models import Listing, Location
from schemas.listings import (
    ListingFilterParams,
    ListingFilterResponse,
    ListingResponse,
    LocationResponse,
    LocationAutocompleteItem,
    LocationAutocompleteResponse,
)

router = APIRouter(prefix="/listings", tags=["Listings"])


def build_listing_conditions(filters: ListingFilterParams):
    """Build filter conditions and determine if Location join is needed"""
    conditions = []
    needs_location_join = False
    
    # Price filters
    if filters.price_min is not None:
        conditions.append(Listing.price_total_zl >= filters.price_min)
    if filters.price_max is not None:
        conditions.append(Listing.price_total_zl <= filters.price_max)
    
    # Price per square meter filters
    if filters.price_sqm_min is not None:
        conditions.append(Listing.price_sqm_zl >= filters.price_sqm_min)
    if filters.price_sqm_max is not None:
        conditions.append(Listing.price_sqm_zl <= filters.price_sqm_max)
    
    # Rooms filter (multi-select)
    if filters.rooms is not None and len(filters.rooms) > 0:
        conditions.append(Listing.rooms.in_(filters.rooms))
    
    # Location filters
    if filters.city is not None:
        conditions.append(Location.city.ilike(f"%{filters.city}%"))
        needs_location_join = True
    
    if filters.city_district is not None:
        conditions.append(Location.city_district.ilike(f"%{filters.city_district}%"))
        needs_location_join = True
    
    return conditions, needs_location_join


async def _filter_listings_impl(
    filters: ListingFilterParams,
    db: AsyncSession,
    limit: int,
    offset: int,
    request_method: str = "GET",
) -> ListingFilterResponse:
    """
    Filter listings based on various criteria:
    - Price range (total and per square meter)
    - Number of rooms (multi-select)
    - Location (city, district)
    
    Returns filtered listings with total count.
    """
    # Build conditions
    conditions, needs_location_join = build_listing_conditions(filters)
    
    # Build count query
    count_query = select(func.count(Listing.listing_id))
    if needs_location_join:
        count_query = count_query.join(Location, Listing.location_id == Location.location_id)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0
    
    # Build data query
    query = select(Listing).options(selectinload(Listing.location))
    if needs_location_join:
        query = query.join(Location, Listing.location_id == Location.location_id)
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get paginated results
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    listings = result.scalars().all()
    
    # Convert to response models
    listing_responses = []
    for listing in listings:
        location_data = listing.location
        location_response = LocationResponse(
            location_id=location_data.location_id,
            city=location_data.city,
            locality=location_data.locality,
            city_district=location_data.city_district,
            street=location_data.street,
            full_address=location_data.full_address,
        )
        
        listing_response = ListingResponse(
            listing_id=listing.listing_id,
            rooms=listing.rooms,
            area=listing.area,
            price_total_zl=listing.price_total_zl,
            price_sqm_zl=listing.price_sqm_zl,
            location=location_response,
        )
        listing_responses.append(listing_response)
    
    response = ListingFilterResponse(
        count=total_count,
        listings=listing_responses,
    )
    
    
    return response


@router.get(
    "/filter",
    response_model=ListingFilterResponse,
    summary="Filter listings (GET)",
    description="Filter real estate listings by price, area, rooms, and location with dynamic result count. Use query parameters.",
)
async def filter_listings_get(
    db: Annotated[AsyncSession, Depends(get_db)],
    price_min: Optional[Decimal] = Query(None, description="Minimum total price in PLN"),
    price_max: Optional[Decimal] = Query(None, description="Maximum total price in PLN"),
    price_sqm_min: Optional[Decimal] = Query(None, description="Minimum price per square meter in PLN"),
    price_sqm_max: Optional[Decimal] = Query(None, description="Maximum price per square meter in PLN"),
    rooms: Optional[List[int]] = Query(None, description="List of room counts (use multiple: rooms=2&rooms=3)"),
    city: Optional[str] = Query(None, description="City name for filtering"),
    city_district: Optional[str] = Query(None, description="City district name for filtering"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
) -> ListingFilterResponse:
    """
    Filter listings based on various criteria (GET method with query parameters):
    - Price range (total and per square meter)
    - Number of rooms (multi-select) - use multiple query params: rooms=2&rooms=3
    - Location (city, district)
    
    Returns filtered listings with total count.
    """
    # #region agent log
    try:
        with open("/Users/mw/project_tools/.cursor/debug.log", "a") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "C",
                "location": "routers/listings.py:filter_listings_get",
                "message": "GET filter endpoint called with query params",
                "data": {
                    "price_min": str(price_min) if price_min else None,
                    "price_max": str(price_max) if price_max else None,
                    "rooms": rooms,
                    "city": city,
                    "city_district": city_district,
                },
                "timestamp": int(__import__("time").time() * 1000),
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    # Build filters object from individual query parameters
    filters = ListingFilterParams(
        price_min=price_min,
        price_max=price_max,
        price_sqm_min=price_sqm_min,
        price_sqm_max=price_sqm_max,
        rooms=rooms,
        city=city,
        city_district=city_district,
    )
    
    return await _filter_listings_impl(filters, db, limit, offset, "GET")


@router.post(
    "/filter",
    response_model=ListingFilterResponse,
    summary="Filter listings (POST)",
    description="Filter real estate listings by price, area, rooms, and location with dynamic result count. Accepts filters in request body. **Use this endpoint when sending filters from frontend with a request body** (browsers don't allow body in GET requests).",
)
async def filter_listings_post(
    filters: ListingFilterParams,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
) -> ListingFilterResponse:
    """
    Filter listings based on various criteria (POST method with request body):
    - Price range (total and per square meter)
    - Number of rooms (multi-select)
    - Location (city, district)
    
    Returns filtered listings with total count.
    
    Use this endpoint when sending complex filter objects from frontend.
    """
    # #region agent log
    try:
        with open("/Users/mw/project_tools/.cursor/debug.log", "a") as f:
            f.write(json.dumps({
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B",
                "location": "routers/listings.py:filter_listings_post",
                "message": "POST filter endpoint called",
                "data": {
                    "filters_received": {
                        "price_min": str(filters.price_min) if filters.price_min else None,
                        "price_max": str(filters.price_max) if filters.price_max else None,
                        "rooms": filters.rooms,
                        "city": filters.city,
                        "city_district": filters.city_district,
                    },
                },
                "timestamp": int(__import__("time").time() * 1000),
            }) + "\n")
    except Exception:
        pass
    # #endregion
    
    return await _filter_listings_impl(filters, db, limit, offset, "POST")


@router.get(
    "/autocomplete/location",
    response_model=LocationAutocompleteResponse,
    summary="Location autocomplete",
    description="Get location suggestions for autocomplete based on search query",
)
async def autocomplete_location(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(..., min_length=1, description="Search query for location"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
) -> LocationAutocompleteResponse:
    """
    Provide location autocomplete suggestions based on city, district, or locality.
    Returns unique locations matching the search query.
    """
    search_pattern = f"%{q}%"
    
    # Search in city, city_district, and locality
    query = (
        select(Location)
        .where(
            or_(
                Location.city.ilike(search_pattern),
                Location.city_district.ilike(search_pattern),
                Location.locality.ilike(search_pattern),
            )
        )
        .distinct()
        .limit(limit)
    )
    
    result = await db.execute(query)
    locations = result.scalars().all()
    
    # Build response with formatted display names
    location_items = []
    seen_combinations = set()
    
    for location in locations:
        # Create display name
        parts = []
        if location.city:
            parts.append(location.city)
        if location.city_district:
            parts.append(location.city_district)
        if location.locality:
            parts.append(location.locality)
        
        display_name = ", ".join(parts) if parts else "Unknown location"
        
        # Avoid duplicates based on display name
        if display_name not in seen_combinations:
            seen_combinations.add(display_name)
            location_items.append(
                LocationAutocompleteItem(
                    location_id=location.location_id,
                    city=location.city,
                    city_district=location.city_district,
                    locality=location.locality,
                    display_name=display_name,
                )
            )
    
    return LocationAutocompleteResponse(locations=location_items)

