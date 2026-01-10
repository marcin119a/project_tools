"""
Script to import listings data from CSV file to database.
Cleans and validates data before inserting into database.
"""
import csv
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.database import async_session_maker
from models.models import Location, Building, Owner, Features, Listing


def clean_string(value: str) -> Optional[str]:
    """Clean string value - strip whitespace and return None if empty."""
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def parse_int(value: str) -> Optional[int]:
    """Parse integer from string, handling spaces and empty values."""
    if not value:
        return None
    if isinstance(value, int):
        return value
    cleaned = str(value).strip().replace(" ", "")
    if not cleaned or cleaned.lower() in ["", "none", "null"]:
        return None
    try:
        return int(cleaned)
    except (ValueError, TypeError):
        return None


def parse_decimal(value: str) -> Optional[Decimal]:
    """Parse decimal from string, handling spaces and empty values."""
    if not value:
        return None
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    cleaned = str(value).strip().replace(" ", "").replace(",", ".")
    if not cleaned or cleaned.lower() in ["", "none", "null", "zapytaj o cenę"]:
        return None
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError, TypeError):
        return None


def parse_boolean(value: str) -> Optional[bool]:
    """Parse boolean from string."""
    if not value:
        return None
    cleaned = str(value).strip().lower()
    if cleaned in ["tak", "yes", "true", "1", "t"]:
        return True
    if cleaned in ["nie", "no", "false", "0", "f", ""]:
        return False
    return None


def parse_floor(value: str) -> Optional[int]:
    """Parse floor number from string (handles 'parter', '3 / winda', etc.)."""
    if not value:
        return None
    cleaned = str(value).strip().lower()
    if cleaned == "parter":
        return 0
    # Extract first number from string like "3 / winda" or "5"
    match = re.search(r"(\d+)", cleaned)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, TypeError):
            return None
    return None


def parse_date(value: str) -> Optional[datetime]:
    """Parse date from Polish text format."""
    if not value:
        return None
    cleaned = str(value).strip().lower()
    
    # Handle relative dates
    today = datetime.now()
    if "wczoraj" in cleaned or "yesterday" in cleaned:
        return today - timedelta(days=1)
    if "dzisiaj" in cleaned or "today" in cleaned:
        return today
    if "ponad tydzień" in cleaned or "over a week" in cleaned:
        return today - timedelta(days=8)
    if "tydzień" in cleaned or "week" in cleaned:
        return today - timedelta(days=7)
    
    # Try to extract days ago
    days_match = re.search(r"(\d+)\s*dni?\s*temu", cleaned)
    if days_match:
        days = int(days_match.group(1))
        return today - timedelta(days=days)
    
    # Try standard date formats
    date_formats = [
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except (ValueError, TypeError):
            continue
    
    return None


async def get_or_create_location(
    session: AsyncSession,
    locality: Optional[str],
    street: Optional[str],
    city_district: Optional[str],
    full_address: Optional[str],
    latitude: Optional[Decimal],
    longitude: Optional[Decimal],
) -> Location:
    """Get existing location or create new one."""
    # Try to find existing location by unique combination
    query = select(Location)
    conditions = []
    
    if locality:
        conditions.append(Location.locality == locality)
    if street:
        conditions.append(Location.street == street)
    if full_address:
        conditions.append(Location.full_address == full_address)
    
    if conditions:
        query = query.where(*conditions)
        result = await session.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            return existing
    
    # Create new location
    location = Location(
        locality=locality,
        street=street,
        city_district=city_district,
        full_address=full_address,
        latitude=latitude,
        longitude=longitude,
    )
    session.add(location)
    await session.flush()
    return location


async def get_or_create_building(
    session: AsyncSession,
    year_built: Optional[int],
    building_type: Optional[str],
    floor: Optional[int],
) -> Building:
    """Get existing building or create new one."""
    # Try to find existing building
    query = select(Building).where(
        Building.year_built == year_built,
        Building.building_type == building_type,
        Building.floor == floor,
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    
    # Create new building
    building = Building(
        year_built=year_built,
        building_type=building_type,
        floor=floor,
    )
    session.add(building)
    await session.flush()
    return building


async def get_or_create_owner(
    session: AsyncSession,
    owner_type: Optional[str],
) -> Owner:
    """Get existing owner or create new one."""
    # Try to find existing owner by type
    query = select(Owner).where(Owner.owner_type == owner_type)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    
    # Create new owner
    owner = Owner(owner_type=owner_type)
    session.add(owner)
    await session.flush()
    return owner


async def get_or_create_features(
    session: AsyncSession,
    has_basement: Optional[bool],
    has_parking: Optional[bool],
    kitchen_type: Optional[str],
    window_type: Optional[str],
    ownership_type: Optional[str],
    equipment: Optional[str],
) -> Features:
    """Get existing features or create new one."""
    # Try to find existing features
    query = select(Features).where(
        Features.has_basement == has_basement,
        Features.has_parking == has_parking,
        Features.kitchen_type == kitchen_type,
        Features.window_type == window_type,
        Features.ownership_type == ownership_type,
        Features.equipment == equipment,
    )
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    
    # Create new features
    features = Features(
        has_basement=has_basement,
        has_parking=has_parking,
        kitchen_type=kitchen_type,
        window_type=window_type,
        ownership_type=ownership_type,
        equipment=equipment,
    )
    session.add(features)
    await session.flush()
    return features


def clean_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Clean and parse a single CSV row."""
    return {
        "locality": clean_string(row.get("locality")),
        "street": clean_string(row.get("street")),
        "city_district": clean_string(row.get("city_district")),
        "full_address": clean_string(row.get("full_address")),
        "latitude": parse_decimal(row.get("latitude")),
        "longitude": parse_decimal(row.get("longitude")),
        "year_built": parse_int(row.get("year_built")),
        "building_type": clean_string(row.get("building_type")),
        "floor": parse_floor(row.get("floor")),
        "owner_type": clean_string(row.get("owner_type")),
        "rooms": parse_int(row.get("rooms")),
        "area": parse_decimal(row.get("area")),
        "price_total_zl": parse_decimal(row.get("price_total_zl")),
        "price_sqm_zl": parse_decimal(row.get("price_sqm_zl")),
        "price_per_sqm_detailed": parse_decimal(row.get("price_per_sqm_detailed")),
        "date_posted": parse_date(row.get("date_posted")),
        "photo_count": parse_int(row.get("photo_count")),
        "url": clean_string(row.get("url")),
        "image_url": clean_string(row.get("image_url")),
        "description_text": clean_string(row.get("description_text")),
        "has_basement": parse_boolean(row.get("has_basement")),
        "has_parking": parse_boolean(row.get("has_parking")),
        "kitchen_type": clean_string(row.get("kitchen_type")),
        "window_type": clean_string(row.get("window_type")),
        "ownership_type": clean_string(row.get("ownership_type")),
        "equipment": clean_string(row.get("equipment")),
    }


async def import_listings_from_csv(csv_path: str, batch_size: int = 100):
    """
    Import listings from CSV file to database.
    
    Args:
        csv_path: Path to CSV file
        batch_size: Number of records to process in one transaction
    """
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    async with async_session_maker() as session:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                batch = []
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header)
                    try:
                        # Skip empty rows
                        if not any(row.values()):
                            skipped_count += 1
                            continue
                        
                        cleaned = clean_row(row)
                        
                        # Skip rows without essential data
                        if not cleaned.get("url"):
                            skipped_count += 1
                            continue
                        
                        batch.append(cleaned)
                        
                        # Process batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            processed = await process_batch(session, batch)
                            imported_count += processed
                            batch = []
                            await session.commit()
                            print(f"Processed {imported_count} listings...")
                    
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing row {row_num}: {e}")
                        continue
                
                # Process remaining batch
                if batch:
                    processed = await process_batch(session, batch)
                    imported_count += processed
                    await session.commit()
            
            print(f"\nImport completed:")
            print(f"  Imported: {imported_count}")
            print(f"  Skipped: {skipped_count}")
            print(f"  Errors: {error_count}")
        
        except Exception as e:
            await session.rollback()
            print(f"Fatal error during import: {e}")
            raise


async def process_batch(session: AsyncSession, batch: list) -> int:
    """Process a batch of cleaned rows."""
    imported = 0
    
    for cleaned in batch:
        try:
            # Get or create related entities
            location = await get_or_create_location(
                session,
                cleaned["locality"],
                cleaned["street"],
                cleaned["city_district"],
                cleaned["full_address"],
                cleaned["latitude"],
                cleaned["longitude"],
            )
            
            building = await get_or_create_building(
                session,
                cleaned["year_built"],
                cleaned["building_type"],
                cleaned["floor"],
            )
            
            owner = await get_or_create_owner(
                session,
                cleaned["owner_type"],
            )
            
            features = await get_or_create_features(
                session,
                cleaned["has_basement"],
                cleaned["has_parking"],
                cleaned["kitchen_type"],
                cleaned["window_type"],
                cleaned["ownership_type"],
                cleaned["equipment"],
            )
            
            # Check if listing with same URL already exists
            existing_query = select(Listing).where(Listing.url == cleaned["url"])
            result = await session.execute(existing_query)
            existing_listing = result.scalar_one_or_none()
            
            if existing_listing:
                # Update existing listing
                existing_listing.location_id = location.location_id
                existing_listing.building_id = building.building_id
                existing_listing.owner_id = owner.owner_id
                existing_listing.features_id = features.features_id
                existing_listing.rooms = cleaned["rooms"]
                existing_listing.area = cleaned["area"]
                existing_listing.price_total_zl = cleaned["price_total_zl"]
                existing_listing.price_sqm_zl = cleaned["price_sqm_zl"]
                existing_listing.price_per_sqm_detailed = cleaned["price_per_sqm_detailed"]
                existing_listing.date_posted = cleaned["date_posted"]
                existing_listing.photo_count = cleaned["photo_count"]
                existing_listing.image_url = cleaned["image_url"]
                existing_listing.description_text = cleaned["description_text"]
            else:
                # Create new listing
                listing = Listing(
                    location_id=location.location_id,
                    building_id=building.building_id,
                    owner_id=owner.owner_id,
                    features_id=features.features_id,
                    rooms=cleaned["rooms"],
                    area=cleaned["area"],
                    price_total_zl=cleaned["price_total_zl"],
                    price_sqm_zl=cleaned["price_sqm_zl"],
                    price_per_sqm_detailed=cleaned["price_per_sqm_detailed"],
                    date_posted=cleaned["date_posted"],
                    photo_count=cleaned["photo_count"],
                    url=cleaned["url"],
                    image_url=cleaned["image_url"],
                    description_text=cleaned["description_text"],
                )
                session.add(listing)
            
            imported += 1
        
        except Exception as e:
            print(f"Error processing listing: {e}")
            continue
    
    return imported


async def main():
    """Main function to run the import."""
    csv_path = "data/ogloszenia_warszawa_detailed.csv"
    print(f"Starting import from {csv_path}...")
    await import_listings_from_csv(csv_path, batch_size=50)


if __name__ == "__main__":
    asyncio.run(main())

