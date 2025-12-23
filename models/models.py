from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Column, Numeric, String, Boolean, Text, Date, SmallInteger, Integer
from sqlmodel import Field, Relationship, SQLModel


class Location(SQLModel, table=True):
    __tablename__ = "location"

    location_id: Optional[int] = Field(default=None, primary_key=True)
    city: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    locality: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    city_district: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    street: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    full_address: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    latitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(9, 6)))
    longitude: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(9, 6)))

    listings: List["Listing"] = Relationship(back_populates="location")


class Building(SQLModel, table=True):
    __tablename__ = "building"

    building_id: Optional[int] = Field(default=None, primary_key=True)
    year_built: Optional[int] = Field(default=None, sa_column=Column(SmallInteger))
    building_type: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    floor: Optional[int] = Field(default=None, sa_column=Column(SmallInteger))

    listings: List["Listing"] = Relationship(back_populates="building")


class Owner(SQLModel, table=True):
    __tablename__ = "owner"

    owner_id: Optional[int] = Field(default=None, primary_key=True)
    owner_type: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    contact_name: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    contact_phone: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    contact_email: Optional[str] = Field(default=None, sa_column=Column(String(255)))

    listings: List["Listing"] = Relationship(back_populates="owner")


class Features(SQLModel, table=True):
    __tablename__ = "features"

    features_id: Optional[int] = Field(default=None, primary_key=True)
    has_basement: Optional[bool] = Field(default=None, sa_column=Column(Boolean))
    has_parking: Optional[bool] = Field(default=None, sa_column=Column(Boolean))
    kitchen_type: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    window_type: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    ownership_type: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    equipment: Optional[str] = Field(default=None, sa_column=Column(Text))

    listings: List["Listing"] = Relationship(back_populates="features")


class Listing(SQLModel, table=True):
    __tablename__ = "listing"

    listing_id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.location_id")
    building_id: int = Field(foreign_key="building.building_id")
    owner_id: int = Field(foreign_key="owner.owner_id")
    features_id: int = Field(foreign_key="features.features_id")
    rooms: Optional[int] = Field(default=None, sa_column=Column(SmallInteger))
    area: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(6, 2)))
    price_total_zl: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 2)))
    price_sqm_zl: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 2)))
    price_per_sqm_detailed: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(12, 2))
    )
    date_posted: Optional[date] = Field(default=None, sa_column=Column(Date))
    photo_count: Optional[int] = Field(default=None, sa_column=Column(Integer))
    url: Optional[str] = Field(default=None, sa_column=Column(Text))
    image_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    description_text: Optional[str] = Field(default=None, sa_column=Column(Text))

    location: Optional[Location] = Relationship(back_populates="listings")
    building: Optional[Building] = Relationship(back_populates="listings")
    owner: Optional[Owner] = Relationship(back_populates="listings")
    features: Optional[Features] = Relationship(back_populates="listings")

