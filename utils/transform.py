"""
Data transformation module implementing SOLID principles.
Contains concrete implementations for data cleaning and transformation.
"""

import pandas as pd
from typing import Dict, Any, Optional

from .interfaces import DataTransformerInterface
from .config import TRANSFORMATION_CONFIG


class RatingCleaner:
    """Single responsibility: Clean rating data."""
    
    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert rating column to float."""
        df = df[df['Rating'] != 'Invalid Rating'].copy()
        df['Rating'] = df['Rating'].str.extract(r'⭐\s*(\d+\.\d+)')
        df['Rating'] = df['Rating'].astype(float)
        return df


class PriceCleaner:
    """Single responsibility: Clean price data."""
    
    def __init__(self, usd_to_idr_rate: Optional[float] = None, decimal_places: Optional[int] = None):
        self.usd_to_idr_rate = usd_to_idr_rate or TRANSFORMATION_CONFIG["usd_to_idr_rate"]
        self.decimal_places = decimal_places or TRANSFORMATION_CONFIG["price_decimal_places"]
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert price column to IDR."""
        df['Price'] = df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df['Price'] = df['Price'].astype(float) * self.usd_to_idr_rate
        df['Price'] = df['Price'].round(self.decimal_places).astype('float64')
        return df


class ColorsCleaner:
    """Single responsibility: Clean colors data."""
    
    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """Convert colors column to integer."""
        df['Colors'] = df['Colors'].str.extract(r'(\d+)').astype(int)
        return df


class AttributeCleaner:
    """Single responsibility: Clean string attributes."""
    
    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """Convert Size and Gender columns to string."""
        df['Size'] = df['Size'].astype(str)
        df['Gender'] = df['Gender'].astype(str)
        return df


class TimestampCleaner:
    """Single responsibility: Clean timestamp data."""
    
    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """Format timestamp to ISO format."""
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S.%f')
        return df


class FashionDataTransformer(DataTransformerInterface):
    """Concrete implementation for fashion data transformation."""
    
    def __init__(self):
        self.rating_cleaner = RatingCleaner()
        self.price_cleaner = PriceCleaner()
        self.colors_cleaner = ColorsCleaner()
        self.attribute_cleaner = AttributeCleaner()
        self.timestamp_cleaner = TimestampCleaner()
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data into cleaned format."""
        try:
            df = data.copy()
            
            # Apply cleaning operations in sequence
            df = self.rating_cleaner.clean(df)
            df = self.price_cleaner.clean(df)
            df = self.colors_cleaner.clean(df)
            df = self.attribute_cleaner.clean(df)
            df = self.timestamp_cleaner.clean(df)
            
            return df
            
        except Exception as e:
            print(f"[Transform Error] Error during data transformation: {e}")
            return pd.DataFrame()


# Legacy function wrapper for backward compatibility
def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy wrapper for FashionDataTransformer."""
    transformer = FashionDataTransformer()
    return transformer.transform(df)
