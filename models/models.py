from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, Date, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

try:
    from .base import Base
except ImportError:
    # Fallback for direct imports (e.g., Alembic)
    from models.base import Base


class Location(Base):
    __tablename__ = "location"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(255), nullable=True)
    locality = Column(String(255), nullable=True)
    city_district = Column(String(255), nullable=True)
    street = Column(String(255), nullable=True)
    full_address = Column(String(500), nullable=True)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)

    # Relationship
    listings = relationship("Listing", back_populates="location")


class Building(Base):
    __tablename__ = "building"

    building_id = Column(Integer, primary_key=True, autoincrement=True)
    year_built = Column(SmallInteger, nullable=True)
    building_type = Column(String(100), nullable=True)
    floor = Column(SmallInteger, nullable=True)

    # Relationship
    listings = relationship("Listing", back_populates="building")


class Owner(Base):
    __tablename__ = "owner"

    owner_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_type = Column(String(50), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)

    # Relationship
    listings = relationship("Listing", back_populates="owner")


class Features(Base):
    __tablename__ = "features"

    features_id = Column(Integer, primary_key=True, autoincrement=True)
    has_basement = Column(Boolean, nullable=True)
    has_parking = Column(Boolean, nullable=True)
    kitchen_type = Column(String(100), nullable=True)
    window_type = Column(String(100), nullable=True)
    ownership_type = Column(String(100), nullable=True)
    equipment = Column(Text, nullable=True)

    # Relationship
    listings = relationship("Listing", back_populates="features")


class Listing(Base):
    __tablename__ = "listing"

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("location.location_id"), nullable=False)
    building_id = Column(Integer, ForeignKey("building.building_id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("owner.owner_id"), nullable=False)
    features_id = Column(Integer, ForeignKey("features.features_id"), nullable=False)
    rooms = Column(SmallInteger, nullable=True)
    area = Column(Numeric(6, 2), nullable=True)
    price_total_zl = Column(Numeric(12, 2), nullable=True)
    price_sqm_zl = Column(Numeric(12, 2), nullable=True)
    price_per_sqm_detailed = Column(Numeric(12, 2), nullable=True)
    date_posted = Column(Date, nullable=True)
    photo_count = Column(Integer, nullable=True)
    url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    description_text = Column(Text, nullable=True)

    # Relationships
    location = relationship("Location", back_populates="listings")
    building = relationship("Building", back_populates="listings")
    owner = relationship("Owner", back_populates="listings")
    features = relationship("Features", back_populates="listings")

