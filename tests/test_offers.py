"""
Tests for offers endpoint sorting functionality.

Tests that GET /offers?sort_by=price&order=desc returns offers
sorted from most expensive to least expensive.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Listing, Location, Building, Owner, Features


@pytest.fixture
async def test_offers_data(test_session: AsyncSession):
    """
    Create test offers data in the database.
    Returns a list of created listing IDs.
    """
    # Create location
    location = Location(
        city="Warszawa",
        locality="Śródmieście",
        full_address="ul. Testowa 1, Warszawa"
    )
    test_session.add(location)
    await test_session.flush()
    
    # Create building
    building = Building(
        year_built=2010,
        building_type="blok",
        floor=5
    )
    test_session.add(building)
    await test_session.flush()
    
    # Create owner
    owner = Owner(
        owner_type="biuro",
        contact_name="Test Owner"
    )
    test_session.add(owner)
    await test_session.flush()
    
    # Create features
    features = Features(
        has_parking=True,
        has_basement=False
    )
    test_session.add(features)
    await test_session.flush()
    
    # Create listings with different prices
    base_date = date.today()
    listings = [
        Listing(
            location_id=location.location_id,
            building_id=building.building_id,
            owner_id=owner.owner_id,
            features_id=features.features_id,
            price_total_zl=Decimal("300000.00"),  # Lowest price
            price_sqm_zl=Decimal("7500.00"),
            area=Decimal("40.00"),
            rooms=2,
            date_posted=base_date - timedelta(days=2),
        ),
        Listing(
            location_id=location.location_id,
            building_id=building.building_id,
            owner_id=owner.owner_id,
            features_id=features.features_id,
            price_total_zl=Decimal("800000.00"),  # Highest price
            price_sqm_zl=Decimal("12000.00"),
            area=Decimal("70.00"),
            rooms=4,
            date_posted=base_date - timedelta(days=1),
        ),
        Listing(
            location_id=location.location_id,
            building_id=building.building_id,
            owner_id=owner.owner_id,
            features_id=features.features_id,
            price_total_zl=Decimal("500000.00"),  # Middle price
            price_sqm_zl=Decimal("10000.00"),
            area=Decimal("50.00"),
            rooms=3,
            date_posted=base_date - timedelta(days=3),
        ),
    ]
    
    for listing in listings:
        test_session.add(listing)
    
    await test_session.commit()
    
    # Return listing IDs for reference
    listing_ids = [listing.listing_id for listing in listings]
    return listing_ids


@pytest.mark.asyncio
async def test_offers_sorted_by_price_descending(sync_test_client: TestClient, test_offers_data):
    """
    Test that GET /offers?sort_by=price&order=desc returns offers
    sorted from most expensive to least expensive.
    """
    # Make request to endpoint
    response = sync_test_client.get("/offers?sort_by=price&order=desc")
    
    # Check status code
    assert response.status_code == 200
    
    # Parse response
    data = response.json()
    
    # Check response structure
    assert "offers" in data
    assert "total" in data
    assert isinstance(data["offers"], list)
    assert data["total"] == 3
    
    # Check that offers are sorted from most expensive to least expensive
    offers = data["offers"]
    prices = [
        Decimal(str(offer["price_total_zl"])) 
        for offer in offers 
        if offer["price_total_zl"] is not None
    ]
    
    # Verify descending order (highest to lowest)
    assert prices == sorted(prices, reverse=True), "Prices should be sorted in descending order"
    
    # Verify specific order: 800000, 500000, 300000
    assert prices[0] == Decimal("800000.00"), "First offer should be most expensive (800000)"
    assert prices[1] == Decimal("500000.00"), "Second offer should be middle price (500000)"
    assert prices[2] == Decimal("300000.00"), "Third offer should be least expensive (300000)"
    
    # Verify that all prices are in correct descending order
    for i in range(len(prices) - 1):
        assert prices[i] >= prices[i + 1], f"Price at index {i} should be >= price at index {i+1}"

