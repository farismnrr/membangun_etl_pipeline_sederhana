"""
Unit tests for data extraction module following SOLID principles.
Tests the new class-based architecture with proper mocking.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.extract import (
    HttpContentFetcher,
    RegexTextExtractor,
    FashionProductParser,
    FashionDataExtractor,
    fetching_content,
    extract_clean_text,
    extract_product_data,
    scrape_fashion_products
)
from utils.config import HEADERS
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time


class TestHttpContentFetcher(unittest.TestCase):
    """Tests for HttpContentFetcher class."""
    
    def setUp(self):
        self.fetcher = HttpContentFetcher()
    
    @patch('utils.extract.requests.get')
    def test_fetch_returns_content_on_success(self, mock_get):
        """Test that fetch returns content on successful HTTP response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test Content</body></html>"
        mock_get.return_value = mock_response
        
        url = "http://example.com"
        content = self.fetcher.fetch(url)
        
        self.assertEqual(content, b"<html><body>Test Content</body></html>")
        mock_get.assert_called_once_with(url, headers=HEADERS)
    
    @patch('utils.extract.requests.get')
    def test_fetch_returns_none_on_failure(self, mock_get):
        """Test that fetch returns None on HTTP request failure."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("HTTP Error")
        mock_get.return_value = mock_response
        
        url = "http://example.com/error"
        content = self.fetcher.fetch(url)
        
        self.assertIsNone(content)
        mock_get.assert_called_once_with(url, headers=HEADERS)


class TestRegexTextExtractor(unittest.TestCase):
    """Tests for RegexTextExtractor class."""
    
    def setUp(self):
        self.extractor = RegexTextExtractor()
    
    def test_extract_text_finds_text(self):
        """Test that extract_text successfully extracts matching text."""
        info_list = [MagicMock(string="Rating: ⭐ 4.5"), MagicMock(string="Colors: 3 Colors")]
        keyword = "Rating"
        pattern = r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)"
        
        result = self.extractor.extract_text(info_list, keyword, pattern)
        self.assertEqual(result, "⭐ 4.5")
    
    def test_extract_text_returns_default_if_not_found(self):
        """Test that extract_text returns default value if keyword not found."""
        info_list = [MagicMock(string="Colors: 3 Colors"), MagicMock(string="Size: M")]
        keyword = "Rating"
        pattern = r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)"
        
        result = self.extractor.extract_text(info_list, keyword, pattern)
        self.assertEqual(result, "N/A")
    
    def test_extract_text_returns_default_if_no_match(self):
        """Test that extract_text returns default value if pattern doesn't match."""
        info_list = [MagicMock(string="Rating Text"), MagicMock(string="Colors: 3 Colors")]
        keyword = "Rating"
        pattern = r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)"
        
        result = self.extractor.extract_text(info_list, keyword, pattern)
        self.assertEqual(result, "N/A")
    
    def test_extract_text_returns_custom_default(self):
        """Test that extract_text returns custom default value."""
        info_list = [MagicMock(string="Some other info")]
        keyword = "NonExistent"
        pattern = r"NonExistent:\s*(.*)"
        default_value = "Not Found"
        
        result = self.extractor.extract_text(info_list, keyword, pattern, default_value)
        self.assertEqual(result, "Not Found")


class TestFashionProductParser(unittest.TestCase):
    """Tests for FashionProductParser class."""
    
    def setUp(self):
        self.text_extractor = RegexTextExtractor()
        self.parser = FashionProductParser(self.text_extractor)
    
    def test_parse_success(self):
        """Test that parse successfully extracts product information."""
        html_content = """
            <div class="collection-card">
                <div class="product-details">
                    <h3 class="product-title">Test Product</h3>
                </div>
                <div class="price-container">$25.00</div>
                <p>Rating: ⭐ 4.8</p>
                <p>Colors: 2 Colors</p>
                <p>Size: L</p>
                <p>Gender: Female</p>
            </div>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        card = soup.find('div', class_='collection-card')
        
        product_data = self.parser.parse(card)
        
        self.assertIsNotNone(product_data)
        self.assertEqual(product_data['Title'], "Test Product")
        self.assertEqual(product_data['Price'], "$25.00")
        self.assertEqual(product_data['Rating'], "⭐ 4.8")
        self.assertEqual(product_data['Colors'], "2")
        self.assertEqual(product_data['Size'], "L")
        self.assertEqual(product_data['Gender'], "Female")
        self.assertIsInstance(product_data['Timestamp'], datetime)
    
    def test_parse_handles_missing_elements(self):
        """Test that parse handles missing HTML elements gracefully."""
        html_content = """
            <div class="collection-card">
                <div class="product-details">
                    <h3 class="product-title">Another Product</h3>
                </div>
            </div>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        card = soup.find('div', class_='collection-card')
        
        product_data = self.parser.parse(card)
        
        self.assertIsNotNone(product_data)
        self.assertEqual(product_data['Title'], "Another Product")
        self.assertEqual(product_data['Price'], "Price Not Available")
        self.assertEqual(product_data['Rating'], "Invalid Rating")
        self.assertEqual(product_data['Colors'], "No Colors")
        self.assertEqual(product_data['Size'], "Unknown")
        self.assertEqual(product_data['Gender'], "Unknown")
        self.assertIsInstance(product_data['Timestamp'], datetime)
    
    def test_parse_handles_empty_title(self):
        """Test that parse handles products with empty titles."""
        html_content = """
            <div class="collection-card">
                <div class="product-details">
                    <h3 class="product-title"></h3>
                </div>
                <div class="price-container">$30.00</div>
                <p>Rating: ⭐ 4.0</p>
            </div>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        card = soup.find('div', class_='collection-card')
        
        product_data = self.parser.parse(card)
        
        self.assertIsNotNone(product_data)
        self.assertEqual(product_data['Title'], "Unknown Title")
        self.assertEqual(product_data['Price'], "$30.00")
        self.assertEqual(product_data['Rating'], "⭐ 4.0")


class TestFashionDataExtractor(unittest.TestCase):
    """Tests for FashionDataExtractor class."""
    
    def setUp(self):
        self.content_fetcher = MagicMock()
        self.product_parser = MagicMock()
        self.extractor = FashionDataExtractor(self.content_fetcher, self.product_parser)
    
    @patch('utils.extract.time.sleep')
    def test_extract_single_page_success(self, mock_sleep):
        """Test successful extraction from a single page."""
        self.content_fetcher.fetch.return_value = b"""
            <html><body>
                <div class="collection-card"></div>
            </body></html>
        """
        
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [MagicMock()]
        
        with patch('utils.extract.BeautifulSoup', return_value=mock_soup):
            self.product_parser.parse.return_value = {"Title": "Test", "Price": "$10"}
            data = self.extractor.extract(total_pages=1, delay=0.1)
            
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['Title'], "Test")
            self.content_fetcher.fetch.assert_called_once()
            self.product_parser.parse.assert_called_once()
            mock_sleep.assert_called_once_with(0.1)


class TestLegacyFunctions(unittest.TestCase):
    """Tests for legacy function wrappers."""
    
    @patch('utils.extract.HttpContentFetcher')
    def test_fetching_content_legacy_wrapper(self, mock_fetcher_class):
        """Test legacy fetching_content function."""
        mock_fetcher = MagicMock()
        mock_fetcher.fetch.return_value = b"content"
        mock_fetcher_class.return_value = mock_fetcher
        
        result = fetching_content("http://test.com")
        
        self.assertEqual(result, b"content")
        mock_fetcher.fetch.assert_called_once_with("http://test.com")
    
    @patch('utils.extract.RegexTextExtractor')
    def test_extract_clean_text_legacy_wrapper(self, mock_extractor_class):
        """Test legacy extract_clean_text function."""
        mock_extractor = MagicMock()
        mock_extractor.extract_text.return_value = "extracted_text"
        mock_extractor_class.return_value = mock_extractor
        
        result = extract_clean_text([], "keyword", "pattern", "default")
        
        self.assertEqual(result, "extracted_text")
        mock_extractor.extract_text.assert_called_once_with([], "keyword", "pattern", "default")


if __name__ == '__main__':
    unittest.main()
