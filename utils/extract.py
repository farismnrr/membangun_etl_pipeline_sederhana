"""
Data extraction module implementing SOLID principles.
Contains concrete implementations for web scraping and data extraction.
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
import requests
from bs4 import BeautifulSoup

from .interfaces import (
    DataExtractorInterface,
    ContentFetcherInterface,
    ProductParserInterface,
    TextExtractorInterface
)
from .config import HEADERS, BASE_URL, EXTRACTION_PATTERNS, DEFAULT_VALUES


class HttpContentFetcher(ContentFetcherInterface):
    """Concrete implementation for fetching HTTP content."""
    
    def __init__(self, headers: Dict[str, str] = None):
        self.headers = headers or HEADERS
    
    def fetch(self, url: str) -> Optional[bytes]:
        """Fetch content from URL with error handling."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
            return None


class RegexTextExtractor(TextExtractorInterface):
    """Concrete implementation for regex-based text extraction."""
    
    def extract_text(self, elements: List, keyword: str, pattern: str, default: str = "N/A") -> str:
        """Extract text using regex pattern and keyword."""
        for element in elements:
            if element.string and keyword in element.string:
                match = re.search(pattern, element.string)
                if match:
                    return match.group(1).strip()
        return default


class FashionProductParser(ProductParserInterface):
    """Concrete implementation for parsing fashion product data."""
    
    def __init__(self, text_extractor: TextExtractorInterface):
        self.text_extractor = text_extractor
    
    def parse(self, html_element) -> Optional[Dict[str, Any]]:
        """Extract product data from HTML card element."""
        try:
            # Extract title
            title_element = html_element.select_one('.product-details h3.product-title')
            title = title_element.text.strip() if title_element and title_element.text.strip() else DEFAULT_VALUES["title"]

            # Extract price
            price_element = html_element.find('div', class_='price-container')
            price = price_element.text.strip() if price_element else DEFAULT_VALUES["price"]

            # Extract info paragraphs
            info_paragraphs = html_element.find_all('p')

            # Extract product attributes using text extractor
            rating = self.text_extractor.extract_text(
                info_paragraphs, "Rating", EXTRACTION_PATTERNS["rating"], DEFAULT_VALUES["rating"]
            )
            colors = self.text_extractor.extract_text(
                info_paragraphs, "Colors", EXTRACTION_PATTERNS["colors"], DEFAULT_VALUES["colors"]
            )
            size = self.text_extractor.extract_text(
                info_paragraphs, "Size", EXTRACTION_PATTERNS["size"], DEFAULT_VALUES["size"]
            )
            gender = self.text_extractor.extract_text(
                info_paragraphs, "Gender", EXTRACTION_PATTERNS["gender"], DEFAULT_VALUES["gender"]
            )

            # Add timestamp
            timestamp = datetime.now()

            return {
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Colors": colors,
                "Size": size,
                "Gender": gender,
                "Timestamp": timestamp
            }

        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None


class FashionDataExtractor(DataExtractorInterface):
    """Concrete implementation for fashion data extraction."""
    
    def __init__(
        self,
        content_fetcher: ContentFetcherInterface,
        product_parser: ProductParserInterface
    ):
        self.content_fetcher = content_fetcher
        self.product_parser = product_parser
    
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape fashion products from multiple pages."""
        total_pages = kwargs.get('total_pages', 50)
        delay = kwargs.get('delay', 2)
        data = []
        
        for page_number in range(1, total_pages + 1):
            url = BASE_URL if page_number == 1 else f"{BASE_URL}page{page_number}"
            
            print(f"Scraping page: {url}")
            content = self.content_fetcher.fetch(url)

            if content:
                try:
                    soup = BeautifulSoup(content, "html.parser")
                    cards = soup.find_all('div', class_='collection-card')
                    
                    if not cards:
                        print(f"No products found on page {page_number}.")
                        continue
                    
                    for card in cards:
                        try:
                            product = self.product_parser.parse(card)
                            if product:
                                data.append(product)
                        except Exception as e:
                            print(f"Error extracting product on page {page_number}: {e}")
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"Error parsing page {page_number}: {e}")
                    continue
            else:
                print(f"Failed to fetch data from page {page_number}, stopping scraping.")
                break

        return data


# Legacy function wrappers for backward compatibility
def fetching_content(url: str) -> Optional[bytes]:
    """Legacy wrapper for HttpContentFetcher."""
    fetcher = HttpContentFetcher()
    return fetcher.fetch(url)


def extract_clean_text(info_list, keyword, pattern, default="N/A") -> str:
    """Legacy wrapper for RegexTextExtractor."""
    extractor = RegexTextExtractor()
    return extractor.extract_text(info_list, keyword, pattern, default)


def extract_product_data(card) -> Optional[Dict[str, Any]]:
    """Legacy wrapper for FashionProductParser."""
    text_extractor = RegexTextExtractor()
    parser = FashionProductParser(text_extractor)
    return parser.parse(card)


def scrape_fashion_products(total_pages: int, delay: int = 2) -> List[Dict[str, Any]]:
    """Legacy wrapper for FashionDataExtractor."""
    content_fetcher = HttpContentFetcher()
    text_extractor = RegexTextExtractor()
    product_parser = FashionProductParser(text_extractor)
    extractor = FashionDataExtractor(content_fetcher, product_parser)
    
    return extractor.extract(total_pages=total_pages, delay=delay)

