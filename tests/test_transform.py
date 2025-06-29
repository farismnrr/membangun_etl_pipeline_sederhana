"""
Unit tests for data transformation module following SOLID principles.
Tests the new class-based architecture with individual cleaners.
"""

import pytest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.transform import (
    RatingCleaner,
    PriceCleaner,
    ColorsCleaner,
    AttributeCleaner,
    TimestampCleaner,
    FashionDataTransformer,
    clean_and_transform
)


class TestRatingCleaner:
    """Tests for RatingCleaner class."""
    
    def test_clean_valid_rating(self):
        """Test cleaning valid rating data."""
        data = {
            "Rating": ["⭐ 4.5", "⭐ 3.9"],
            "Other": ["A", "B"]
        }
        df = pd.DataFrame(data)
        result = RatingCleaner.clean(df)
        
        assert not result.empty
        assert result["Rating"].dtype == float
        assert len(result) == 2
    
    def test_clean_filters_invalid_rating(self):
        """Test that invalid ratings are filtered out."""
        data = {
            "Rating": ["⭐ 4.5", "Invalid Rating"],
            "Other": ["A", "B"]
        }
        df = pd.DataFrame(data)
        result = RatingCleaner.clean(df)
        
        assert len(result) == 1
        assert result["Rating"].iloc[0] == 4.5


class TestPriceCleaner:
    """Tests for PriceCleaner class."""
    
    def test_clean_default_rate(self):
        """Test price cleaning with default USD to IDR rate."""
        data = {
            "Price": ["$10.00", "$20.00"],
            "Other": ["A", "B"]
        }
        df = pd.DataFrame(data)
        cleaner = PriceCleaner()
        result = cleaner.clean(df)
        
        assert not result.empty
        assert result["Price"].dtype == float
        assert result["Price"].iloc[0] == 160000.0  # 10 * 16000
    
    def test_clean_custom_rate(self):
        """Test price cleaning with custom conversion rate."""
        data = {
            "Price": ["$10.00"],
            "Other": ["A"]
        }
        df = pd.DataFrame(data)
        cleaner = PriceCleaner(usd_to_idr_rate=15000, decimal_places=0)
        result = cleaner.clean(df)
        
        assert result["Price"].iloc[0] == 150000.0


class TestColorsCleaner:
    """Tests for ColorsCleaner class."""
    
    def test_clean_colors(self):
        """Test colors cleaning and conversion to integer."""
        data = {
            "Colors": ["3 Colors", "5 Colors"],
            "Other": ["A", "B"]
        }
        df = pd.DataFrame(data)
        result = ColorsCleaner.clean(df)
        
        assert not result.empty
        assert result["Colors"].dtype == int
        assert result["Colors"].iloc[0] == 3
        assert result["Colors"].iloc[1] == 5


class TestAttributeCleaner:
    """Tests for AttributeCleaner class."""
    
    def test_clean_attributes(self):
        """Test attribute cleaning and string conversion."""
        data = {
            "Size": ["M", "L"],
            "Gender": ["Male", "Female"],
            "Other": ["A", "B"]
        }
        df = pd.DataFrame(data)
        result = AttributeCleaner.clean(df)
        
        assert not result.empty
        assert pd.api.types.is_string_dtype(result["Size"])
        assert pd.api.types.is_string_dtype(result["Gender"])


class TestTimestampCleaner:
    """Tests for TimestampCleaner class."""
    
    def test_clean_timestamp(self):
        """Test timestamp cleaning and ISO format conversion."""
        data = {
            "Timestamp": ["2025-05-10 10:00:00", "2025-05-10 11:00:00"],
            "Other": ["A", "B"]
        }
        df = pd.DataFrame(data)
        result = TimestampCleaner.clean(df)
        
        assert not result.empty
        assert result["Timestamp"].str.contains("T").all()


class TestFashionDataTransformer:
    """Tests for FashionDataTransformer class."""
    
    def test_transform_valid_data(self):
        """Test complete transformation of valid data."""
        data = {
            "Title": ["Item A", "Item B"],
            "Price": ["$10.00", "$20.00"],
            "Rating": ["⭐ 4.5", "⭐ 3.9"],
            "Colors": ["3 Colors", "5 Colors"],
            "Size": ["M", "L"],
            "Gender": ["Male", "Female"],
            "Timestamp": ["2025-05-10 10:00:00", "2025-05-10 11:00:00"]
        }
        df = pd.DataFrame(data)
        transformer = FashionDataTransformer()
        result = transformer.transform(df)

        assert not result.empty
        assert result["Rating"].dtype == float
        assert result["Price"].dtype == float
        assert result["Colors"].dtype == int
        assert pd.api.types.is_string_dtype(result["Size"])
        assert pd.api.types.is_string_dtype(result["Gender"])
        assert result["Timestamp"].str.contains("T").all()
    
    def test_transform_invalid_rating(self):
        """Test transformation with invalid rating data."""
        data = {
            "Title": ["Item A"],
            "Price": ["$10.00"],
            "Rating": ["Invalid Rating"],
            "Colors": ["3 Colors"],
            "Size": ["M"],
            "Gender": ["Male"],
            "Timestamp": ["2025-05-10 10:00:00"]
        }
        df = pd.DataFrame(data)
        transformer = FashionDataTransformer()
        result = transformer.transform(df)

        # Row should be removed due to invalid rating
        assert result.empty
    
    def test_transform_malformed_price(self):
        """Test transformation with malformed price data."""
        data = {
            "Title": ["Item A"],
            "Price": ["INVALID"],
            "Rating": ["⭐ 4.0"],
            "Colors": ["3 Colors"],
            "Size": ["M"],
            "Gender": ["Male"],
            "Timestamp": ["2025-05-10 10:00:00"]
        }
        df = pd.DataFrame(data)
        transformer = FashionDataTransformer()
        result = transformer.transform(df)

        # Should return empty DataFrame on transformation error
        assert result.empty


class TestLegacyFunction:
    """Tests for legacy function wrapper."""
    
    def test_clean_and_transform_legacy_wrapper(self):
        """Test legacy clean_and_transform function."""
        data = {
            "Title": ["Item A"],
            "Price": ["$10.00"],
            "Rating": ["⭐ 4.5"],
            "Colors": ["3 Colors"],
            "Size": ["M"],
            "Gender": ["Male"],
            "Timestamp": ["2025-05-10 10:00:00"]
        }
        df = pd.DataFrame(data)
        result = clean_and_transform(df)

        assert not result.empty
        assert result["Rating"].dtype == float
        assert result["Price"].dtype == float
