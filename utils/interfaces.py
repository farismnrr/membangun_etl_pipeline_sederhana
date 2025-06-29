"""
Interfaces for the ETL pipeline following SOLID principles.
This module defines abstract base classes for data extraction, transformation, and loading.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd


class DataExtractorInterface(ABC):
    """Interface for data extraction operations."""
    
    @abstractmethod
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract data from a source."""
        pass


class DataTransformerInterface(ABC):
    """Interface for data transformation operations."""
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data into cleaned format."""
        pass


class DataLoaderInterface(ABC):
    """Interface for data loading operations."""
    
    @abstractmethod
    def load(self, data: pd.DataFrame, **kwargs) -> bool:
        """Load data to a destination."""
        pass


class ContentFetcherInterface(ABC):
    """Interface for fetching content from web sources."""
    
    @abstractmethod
    def fetch(self, url: str) -> Optional[bytes]:
        """Fetch content from a URL."""
        pass


class ProductParserInterface(ABC):
    """Interface for parsing product data from HTML."""
    
    @abstractmethod
    def parse(self, html_element) -> Optional[Dict[str, Any]]:
        """Parse product data from HTML element."""
        pass


class TextExtractorInterface(ABC):
    """Interface for extracting text using patterns."""
    
    @abstractmethod
    def extract_text(self, elements: List, keyword: str, pattern: str, default: str = "N/A") -> str:
        """Extract text based on keyword and pattern."""
        pass
