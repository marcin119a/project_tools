"""
OfferSorter class for sorting listing offers based on various criteria.

Implements sorting functionality according to User Story 4.3:
- Price (ascending/descending)
- Price per square meter (ascending/descending)
- Date posted (newest first)
- Area (ascending/descending)
- Default: "Najtrafniejsze" (relevance-based, returns unchanged list)
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Tuple
from decimal import Decimal
from datetime import date


class SortOption(str, Enum):
    """Enumeration of available sorting options."""
    
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    PRICE_PER_SQM_ASC = "price_per_sqm_asc"
    PRICE_PER_SQM_DESC = "price_per_sqm_desc"
    DATE_NEWEST = "date_newest"
    AREA_ASC = "area_asc"
    AREA_DESC = "area_desc"
    NAJTRAFNIEJSZE = "najtrafniejsze"


class OfferSorter:
    """Class for sorting listing offers based on various criteria."""
    
    # Maximum values for None handling
    MAX_PRICE = Decimal("999999999999.99")
    MAX_AREA = Decimal("999999999.99")
    
    def __init__(self):
        """Initialize OfferSorter with sort strategy mapping."""
        self._sort_strategies: Dict[str, Tuple[Callable[[Dict[str, Any]], Any], bool]] = {
            SortOption.PRICE_ASC.value: (self._get_price_value, False),
            SortOption.PRICE_DESC.value: (self._get_price_value, True),
            SortOption.PRICE_PER_SQM_ASC.value: (self._get_price_per_sqm_value, False),
            SortOption.PRICE_PER_SQM_DESC.value: (self._get_price_per_sqm_value, True),
            SortOption.DATE_NEWEST.value: (self._get_date_value, True),
            SortOption.AREA_ASC.value: (self._get_area_value, False),
            SortOption.AREA_DESC.value: (self._get_area_value, True),
        }
    
    def sort(
        self, 
        offers: List[Dict[str, Any]], 
        sort_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Sort offers based on the specified criteria.
        
        Args:
            offers: List of offer dictionaries to sort
            sort_by: Sorting criteria. Can be string or SortOption enum value.
                Options:
                - "price_asc": Price ascending
                - "price_desc": Price descending
                - "price_per_sqm_asc": Price per square meter ascending
                - "price_per_sqm_desc": Price per square meter descending
                - "date_newest": Date posted, newest first
                - "area_asc": Area ascending
                - "area_desc": Area descending
                - "najtrafniejsze" or None: Default relevance-based (unchanged)
        
        Returns:
            Sorted list of offers (new list, original is not modified)
        
        Raises:
            ValueError: If sort_by is not a valid option
        """
        if not offers:
            return []
        
        # Normalize sort_by to string
        sort_key = self._normalize_sort_option(sort_by)
        
        # Default sorting: return unchanged list
        if sort_key is None or sort_key == SortOption.NAJTRAFNIEJSZE.value:
            return offers.copy()
        
        # Validate sort option
        if sort_key not in self._sort_strategies:
            raise ValueError(f"Invalid sort option: {sort_by}")
        
        # Get sort strategy
        key_func, reverse = self._sort_strategies[sort_key]
        
        # Create a copy and sort
        sorted_offers = offers.copy()
        sorted_offers.sort(key=key_func, reverse=reverse)
        
        return sorted_offers
    
    def _normalize_sort_option(self, sort_by: Optional[str]) -> Optional[str]:
        """
        Normalize sort option to string value.
        
        Args:
            sort_by: Sort option as string or None
        
        Returns:
            Normalized string value or None
        """
        if sort_by is None:
            return None
        
        # Convert enum to string if needed
        if isinstance(sort_by, SortOption):
            return sort_by.value
        
        return sort_by
    
    def _get_price_value(self, offer: Dict[str, Any]) -> Decimal:
        """
        Extract price value from offer, handling None values.
        
        None values are treated as maximum value to place them at the end
        when sorting ascending, or at the beginning when sorting descending.
        
        Args:
            offer: Offer dictionary
        
        Returns:
            Price as Decimal, or MAX_PRICE if None
        """
        price = offer.get("price_total_zl")
        if price is None:
            return self.MAX_PRICE
        return Decimal(str(price))
    
    def _calculate_price_per_sqm(
        self, 
        price_total: Optional[Decimal], 
        area: Optional[Decimal]
    ) -> Optional[Decimal]:
        """
        Calculate price per square meter from total price and area.
        
        Args:
            price_total: Total price as Decimal or None
            area: Area as Decimal or None
        
        Returns:
            Calculated price per square meter as Decimal, or None if cannot calculate
        """
        if price_total is None or area is None or area == 0:
            return None
        return Decimal(str(price_total)) / Decimal(str(area))
    
    def _get_price_per_sqm_value(self, offer: Dict[str, Any]) -> Decimal:
        """
        Extract price per square meter value from offer.
        
        First tries price_sqm_zl, if not available calculates from price_total_zl / area.
        Handles None values.
        
        Args:
            offer: Offer dictionary
        
        Returns:
            Price per square meter as Decimal, or MAX_PRICE if cannot determine
        """
        # Try to get price_sqm_zl directly
        price_per_sqm = offer.get("price_sqm_zl")
        if price_per_sqm is not None:
            return Decimal(str(price_per_sqm))
        
        # Calculate from price_total_zl / area if price_sqm_zl is not available
        price_total = offer.get("price_total_zl")
        area = offer.get("area")
        
        calculated_price = self._calculate_price_per_sqm(price_total, area)
        if calculated_price is not None:
            return calculated_price
        
        # If cannot calculate, treat as maximum value
        return self.MAX_PRICE
    
    def _get_date_value(self, offer: Dict[str, Any]) -> date:
        """
        Extract date value from offer, handling None values.
        
        None values are treated as minimum date to place them at the end
        when sorting by newest first.
        """
        date_posted = offer.get("date_posted")
        if date_posted is None:
            # Use minimum date to place None at the end when sorting newest first
            return date.min
        # Return date_posted as-is (should already be a date object)
        return date_posted
    
    def _get_area_value(self, offer: Dict[str, Any]) -> Decimal:
        """
        Extract area value from offer, handling None values.
        
        None values are treated as maximum value to place them at the end
        when sorting ascending, or at the beginning when sorting descending.
        
        Args:
            offer: Offer dictionary
        
        Returns:
            Area as Decimal, or MAX_AREA if None
        """
        area = offer.get("area")
        if area is None:
            return self.MAX_AREA
        return Decimal(str(area))

