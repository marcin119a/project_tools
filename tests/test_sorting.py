"""
Tests for OfferSorter class based on User Story 4.3 (Sortowanie).

User Story: Jako użytkownik chcę mieć możliwość zmiany kolejności wyświetlanych ofert,
aby najpierw widzieć te najtańsze, najnowsze lub o najlepszym stosunku ceny do metrażu.

Kryteria akceptacji:
- Cena (rosnąco/malejąco)
- Cena za m² (rosnąco/malejąco)
- Data dodania (najnowsze)
- Metraż (rosnąco/malejąco)
- Domyślne sortowanie: "Najtrafniejsze"
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from utils.sorter import OfferSorter


@pytest.fixture
def mock_offers():
    """Create mock offer data for testing."""
    base_date = date.today()
    
    return [
        {
            "listing_id": 1,
            "price_total_zl": Decimal("500000.00"),
            "price_sqm_zl": Decimal("10000.00"),
            "area": Decimal("50.00"),
            "date_posted": base_date - timedelta(days=5),
        },
        {
            "listing_id": 2,
            "price_total_zl": Decimal("300000.00"),
            "price_sqm_zl": Decimal("7500.00"),
            "area": Decimal("40.00"),
            "date_posted": base_date - timedelta(days=2),
        },
        {
            "listing_id": 3,
            "price_total_zl": Decimal("800000.00"),
            "price_sqm_zl": Decimal("12000.00"),
            "area": Decimal("70.00"),
            "date_posted": base_date - timedelta(days=1),  # Most recent
        },
        {
            "listing_id": 4,
            "price_total_zl": Decimal("400000.00"),
            "price_sqm_zl": Decimal("8000.00"),
            "area": Decimal("60.00"),
            "date_posted": base_date - timedelta(days=10),
        },
        {
            "listing_id": 5,
            "price_total_zl": Decimal("600000.00"),
            "price_sqm_zl": Decimal("15000.00"),
            "area": Decimal("30.00"),
            "date_posted": base_date - timedelta(days=3),
        },
    ]


class TestOfferSorterPrice:
    """Test sorting by price (ascending/descending)."""
    
    def test_sort_by_price_ascending(self, mock_offers):
        """Test sorting offers by price in ascending order."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="price_asc")
        
        assert len(sorted_offers) == len(mock_offers)
        prices = [offer["price_total_zl"] for offer in sorted_offers]
        assert prices == sorted(prices)
        assert sorted_offers[0]["listing_id"] == 2  # Lowest price: 300000
        assert sorted_offers[-1]["listing_id"] == 3  # Highest price: 800000
    
    def test_sort_by_price_descending(self, mock_offers):
        """Test sorting offers by price in descending order."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="price_desc")
        
        assert len(sorted_offers) == len(mock_offers)
        prices = [offer["price_total_zl"] for offer in sorted_offers]
        assert prices == sorted(prices, reverse=True)
        assert sorted_offers[0]["listing_id"] == 3  # Highest price: 800000
        assert sorted_offers[-1]["listing_id"] == 2  # Lowest price: 300000
    
    def test_sort_by_price_ascending_with_duplicates(self, mock_offers):
        """Test sorting by price when multiple offers have the same price."""
        # Add duplicate price
        mock_offers.append({
            "listing_id": 6,
            "price_total_zl": Decimal("300000.00"),
            "price_sqm_zl": Decimal("8000.00"),
            "area": Decimal("35.00"),
            "date_posted": date.today() - timedelta(days=7),
        })
        
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="price_asc")
        
        prices = [offer["price_total_zl"] for offer in sorted_offers]
        assert prices == sorted(prices)
        assert sorted_offers[0]["price_total_zl"] == Decimal("300000.00")
        assert sorted_offers[1]["price_total_zl"] == Decimal("300000.00")


class TestOfferSorterPricePerSqm:
    """Test sorting by price per square meter (ascending/descending)."""
    
    def test_sort_by_price_per_sqm_ascending(self, mock_offers):
        """Test sorting offers by price per square meter in ascending order."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="price_per_sqm_asc")
        
        assert len(sorted_offers) == len(mock_offers)
        prices_per_sqm = [offer["price_sqm_zl"] for offer in sorted_offers]
        assert prices_per_sqm == sorted(prices_per_sqm)
        assert sorted_offers[0]["listing_id"] == 2  # Lowest: 7500
        assert sorted_offers[-1]["listing_id"] == 5  # Highest: 15000
    
    def test_sort_by_price_per_sqm_descending(self, mock_offers):
        """Test sorting offers by price per square meter in descending order."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="price_per_sqm_desc")
        
        assert len(sorted_offers) == len(mock_offers)
        prices_per_sqm = [offer["price_sqm_zl"] for offer in sorted_offers]
        assert prices_per_sqm == sorted(prices_per_sqm, reverse=True)
        assert sorted_offers[0]["listing_id"] == 5  # Highest: 15000
        assert sorted_offers[-1]["listing_id"] == 2  # Lowest: 7500


class TestOfferSorterDatePosted:
    """Test sorting by date posted (newest first)."""
    
    def test_sort_by_date_newest_first(self, mock_offers):
        """Test sorting offers by date posted, newest first."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="date_newest")
        
        assert len(sorted_offers) == len(mock_offers)
        dates = [offer["date_posted"] for offer in sorted_offers]
        assert dates == sorted(dates, reverse=True)
        assert sorted_offers[0]["listing_id"] == 3  # Most recent
        assert sorted_offers[-1]["listing_id"] == 4  # Oldest
    
    def test_sort_by_date_with_same_dates(self, mock_offers):
        """Test sorting by date when multiple offers have the same date."""
        base_date = date.today()
        mock_offers.append({
            "listing_id": 6,
            "price_total_zl": Decimal("350000.00"),
            "price_sqm_zl": Decimal("9000.00"),
            "area": Decimal("45.00"),
            "date_posted": base_date - timedelta(days=1),  # Same as listing_id 3
        })
        
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="date_newest")
        
        dates = [offer["date_posted"] for offer in sorted_offers]
        assert dates == sorted(dates, reverse=True)
        assert sorted_offers[0]["date_posted"] == base_date - timedelta(days=1)


class TestOfferSorterArea:
    """Test sorting by area (ascending/descending)."""
    
    def test_sort_by_area_ascending(self, mock_offers):
        """Test sorting offers by area in ascending order."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="area_asc")
        
        assert len(sorted_offers) == len(mock_offers)
        areas = [offer["area"] for offer in sorted_offers]
        assert areas == sorted(areas)
        assert sorted_offers[0]["listing_id"] == 5  # Smallest: 30.00
        assert sorted_offers[-1]["listing_id"] == 3  # Largest: 70.00
    
    def test_sort_by_area_descending(self, mock_offers):
        """Test sorting offers by area in descending order."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="area_desc")
        
        assert len(sorted_offers) == len(mock_offers)
        areas = [offer["area"] for offer in sorted_offers]
        assert areas == sorted(areas, reverse=True)
        assert sorted_offers[0]["listing_id"] == 3  # Largest: 70.00
        assert sorted_offers[-1]["listing_id"] == 5  # Smallest: 30.00


class TestOfferSorterDefault:
    """Test default sorting (Najtrafniejsze - relevance-based)."""
    
    def test_default_sorting_najtrafniejsze(self, mock_offers):
        """Test that default sorting uses 'Najtrafniejsze' algorithm."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers)
        
        assert len(sorted_offers) == len(mock_offers)
        # Default sorting should return offers in relevance order
        # (implementation-specific, but should not raise error)
        assert all(offer in mock_offers for offer in sorted_offers)
    
    def test_default_sorting_with_explicit_najtrafniejsze(self, mock_offers):
        """Test explicit 'Najtrafniejsze' sorting option."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="najtrafniejsze")
        
        assert len(sorted_offers) == len(mock_offers)
        assert all(offer in mock_offers for offer in sorted_offers)


class TestOfferSorterEdgeCases:
    """Test edge cases and error handling."""
    
    def test_sort_empty_list(self):
        """Test sorting an empty list of offers."""
        sorter = OfferSorter()
        sorted_offers = sorter.sort([])
        
        assert sorted_offers == []
    
    def test_sort_single_offer(self):
        """Test sorting a list with a single offer."""
        single_offer = [{
            "listing_id": 1,
            "price_total_zl": Decimal("500000.00"),
            "price_sqm_zl": Decimal("10000.00"),
            "area": Decimal("50.00"),
            "date_posted": date.today(),
        }]
        
        sorter = OfferSorter()
        sorted_offers = sorter.sort(single_offer, sort_by="price_asc")
        
        assert len(sorted_offers) == 1
        assert sorted_offers[0]["listing_id"] == 1
    
    def test_sort_with_none_values(self):
        """Test sorting when some offers have None values."""
        offers_with_none = [
            {
                "listing_id": 1,
                "price_total_zl": Decimal("500000.00"),
                "price_sqm_zl": Decimal("10000.00"),
                "area": Decimal("50.00"),
                "date_posted": date.today(),
            },
            {
                "listing_id": 2,
                "price_total_zl": None,
                "price_sqm_zl": None,
                "area": None,
                "date_posted": None,
            },
            {
                "listing_id": 3,
                "price_total_zl": Decimal("300000.00"),
                "price_sqm_zl": Decimal("7500.00"),
                "area": Decimal("40.00"),
                "date_posted": date.today() - timedelta(days=1),
            },
        ]
        
        sorter = OfferSorter()
        sorted_offers = sorter.sort(offers_with_none, sort_by="price_asc")
        
        assert len(sorted_offers) == 3
        # Offers with None values should be handled appropriately
        # (either filtered out or placed at the end/beginning)
    
    def test_sort_with_invalid_sort_option(self, mock_offers):
        """Test sorting with an invalid sort option."""
        sorter = OfferSorter()
        
        with pytest.raises(ValueError, match="Invalid sort option"):
            sorter.sort(mock_offers, sort_by="invalid_option")
    
    def test_sort_preserves_original_list(self, mock_offers):
        """Test that sorting does not modify the original list."""
        original_offers = mock_offers.copy()
        sorter = OfferSorter()
        sorted_offers = sorter.sort(mock_offers, sort_by="price_asc")
        
        assert mock_offers == original_offers
        assert sorted_offers != original_offers  # Should be sorted differently

