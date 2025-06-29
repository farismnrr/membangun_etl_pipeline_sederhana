"""
Integration tests for the main ETL pipeline following SOLID principles.
Tests the complete ETL workflow with proper mocking.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import ETLPipeline, main
import pandas as pd


class TestETLPipeline(unittest.TestCase):
    """Tests for ETLPipeline class."""
    
    def setUp(self):
        self.pipeline = ETLPipeline()
    
    @patch('main.FashionDataExtractor')
    def test_extract_data_success(self, mock_extractor_class):
        """Test successful data extraction."""
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = [
            {"Title": "Test Product", "Price": "$10.00", "Rating": "⭐ 4.5"}
        ]
        mock_extractor_class.return_value = mock_extractor
        
        pipeline = ETLPipeline()
        result = pipeline.extract_data(total_pages=1)
        
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Title'], "Test Product")
    
    @patch('main.FashionDataExtractor')
    def test_extract_data_empty_result(self, mock_extractor_class):
        """Test data extraction with empty result."""
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = []
        mock_extractor_class.return_value = mock_extractor
        
        pipeline = ETLPipeline()
        result = pipeline.extract_data(total_pages=1)
        
        self.assertTrue(result.empty)
    
    @patch('main.FashionDataTransformer')
    def test_transform_data_success(self, mock_transformer_class):
        """Test successful data transformation."""
        mock_transformer = MagicMock()
        mock_transformed_df = pd.DataFrame({
            "Title": ["Test Product"],
            "Price": [160000.0],
            "Rating": [4.5]
        })
        mock_transformer.transform.return_value = mock_transformed_df
        mock_transformer_class.return_value = mock_transformer
        
        pipeline = ETLPipeline()
        input_df = pd.DataFrame({
            "Title": ["Test Product"],
            "Price": ["$10.00"],
            "Rating": ["⭐ 4.5"]
        })
        
        result = pipeline.transform_data(input_df)
        
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]['Price'], 160000.0)
        self.assertEqual(result.iloc[0]['Rating'], 4.5)
    
    def test_transform_data_empty_input(self):
        """Test data transformation with empty input."""
        pipeline = ETLPipeline()
        empty_df = pd.DataFrame()
        
        result = pipeline.transform_data(empty_df)
        
        self.assertTrue(result.empty)
    
    @patch('main.MultiDestinationDataLoader')
    def test_load_data_success(self, mock_loader_class):
        """Test successful data loading."""
        mock_loader = MagicMock()
        mock_loader.load_to_all.return_value = {
            'csv': True,
            'postgresql': True,
            'google_sheets': True
        }
        mock_loader_class.return_value = mock_loader
        
        pipeline = ETLPipeline()
        test_df = pd.DataFrame({
            "Title": ["Test Product"],
            "Price": [160000.0]
        })
        
        # Should not raise any exceptions
        pipeline.load_data(test_df)
        
        mock_loader.load_to_all.assert_called_once_with(test_df)
    
    def test_load_data_empty_input(self):
        """Test data loading with empty input."""
        pipeline = ETLPipeline()
        empty_df = pd.DataFrame()
        
        # Should not raise any exceptions and should print appropriate message
        pipeline.load_data(empty_df)
    
    @patch('main.ETLPipeline.load_data')
    @patch('main.ETLPipeline.transform_data')
    @patch('main.ETLPipeline.extract_data')
    def test_run_complete_pipeline(self, mock_extract, mock_transform, mock_load):
        """Test complete ETL pipeline execution."""
        # Setup mocks
        raw_df = pd.DataFrame({"Title": ["Test"], "Price": ["$10.00"]})
        cleaned_df = pd.DataFrame({"Title": ["Test"], "Price": [160000.0]})
        
        mock_extract.return_value = raw_df
        mock_transform.return_value = cleaned_df
        mock_load.return_value = None
        
        pipeline = ETLPipeline()
        
        # Should not raise any exceptions
        pipeline.run(total_pages=1)
        
        mock_extract.assert_called_once_with(1)
        mock_transform.assert_called_once_with(raw_df)
        mock_load.assert_called_once_with(cleaned_df)
    
    @patch('main.ETLPipeline.extract_data', side_effect=Exception("Extraction failed"))
    def test_run_with_exception(self, mock_extract):
        """Test ETL pipeline execution with exception."""
        pipeline = ETLPipeline()
        
        # Should handle exception gracefully
        pipeline.run(total_pages=1)
        
        mock_extract.assert_called_once()


class TestMainFunction(unittest.TestCase):
    """Tests for main function."""
    
    @patch('main.ETLPipeline')
    def test_main_function(self, mock_pipeline_class):
        """Test main function execution."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        main()
        
        mock_pipeline_class.assert_called_once()
        mock_pipeline.run.assert_called_once_with(total_pages=50)


if __name__ == '__main__':
    unittest.main()
