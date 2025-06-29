"""
Unit tests for data loading module following SOLID principles.
Tests the new class-based architecture with separate loaders.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.load import (
    CsvDataLoader,
    PostgreSQLDataLoader,
    GoogleSheetsDataLoader,
    MultiDestinationDataLoader,
    save_to_csv,
    save_to_postgresql,
    save_to_google_spreadsheet,
    load_data
)


# Fixture DataFrame
@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Title": ["Item A"],
        "Price": [160000.0],
        "Rating": [4.5],
        "Colors": [3],
        "Size": ["M"],
        "Gender": ["Male"],
        "Timestamp": ["2025-05-10T10:00:00.000000"]
    })


class TestCsvDataLoader:
    """Tests for CsvDataLoader class."""
    
    def test_load_success(self, tmp_path, sample_dataframe):
        """Test successful CSV file loading."""
        file_path = tmp_path / "test_fashion.csv"
        loader = CsvDataLoader()
        
        result = loader.load(sample_dataframe, filename=str(file_path))
        
        assert result is True
        assert file_path.exists()
        df_read = pd.read_csv(file_path)
        assert not df_read.empty
        assert list(df_read.columns) == list(sample_dataframe.columns)
    
    @patch("pandas.DataFrame.to_csv", side_effect=Exception("Disk full"))
    def test_load_exception(self, mock_to_csv, sample_dataframe, capsys):
        """Test CSV loading exception handling."""
        loader = CsvDataLoader()
        result = loader.load(sample_dataframe, filename="test_fashion.csv")
        
        assert result is False
        captured = capsys.readouterr()
        assert "[CSV Error] Failed to save data to CSV: Disk full" in captured.out


class TestPostgreSQLDataLoader:
    """Tests for PostgreSQLDataLoader class."""
    
    @patch("utils.load.create_engine")
    def test_load_success(self, mock_create_engine, sample_dataframe):
        """Test successful PostgreSQL loading."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        loader = PostgreSQLDataLoader()
        
        with patch.object(sample_dataframe, 'to_sql') as mock_to_sql:
            result = loader.load(
                sample_dataframe,
                db_name="test_db",
                user="user",
                password="password"
            )
            
            assert result is True
            mock_to_sql.assert_called_once_with(
                "fashion_products", mock_engine, index=False, if_exists="append"
            )
    
    @patch("utils.load.create_engine", side_effect=Exception("Connection failed"))
    def test_load_exception(self, mock_create_engine, sample_dataframe, capsys):
        """Test PostgreSQL loading exception handling."""
        loader = PostgreSQLDataLoader()
        result = loader.load(
            sample_dataframe,
            db_name="invalid_db",
            user="invalid_user",
            password="invalid_pass"
        )
        
        assert result is False
        captured = capsys.readouterr()
        assert "[PostgreSQL Error]" in captured.out


class TestGoogleSheetsDataLoader:
    """Tests for GoogleSheetsDataLoader class."""
    
    @patch("utils.load.Credentials.from_service_account_file")
    @patch("utils.load.build")
    def test_load_success(self, mock_build, mock_creds, sample_dataframe):
        """Test successful Google Sheets loading."""
        mock_service = MagicMock()
        mock_spreadsheets = MagicMock()
        mock_values = MagicMock()

        mock_service.spreadsheets.return_value = mock_spreadsheets
        mock_spreadsheets.values.return_value = mock_values
        mock_values.clear.return_value.execute.return_value = None
        mock_values.update.return_value.execute.return_value = None
        mock_build.return_value = mock_service
        
        loader = GoogleSheetsDataLoader()
        result = loader.load(
            sample_dataframe,
            spreadsheet_id="fake_id",
            range_name="Sheet1!A1",
            credential_file="fake_credential.json"
        )
        
        assert result is True
        mock_creds.assert_called_once()
        mock_build.assert_called_once_with("sheets", "v4", credentials=mock_creds.return_value)
        assert mock_values.clear.called
        assert mock_values.update.called
    
    @patch("utils.load.Credentials.from_service_account_file", side_effect=Exception("Invalid credentials"))
    def test_load_exception(self, mock_creds, sample_dataframe, capsys):
        """Test Google Sheets loading exception handling."""
        loader = GoogleSheetsDataLoader()
        result = loader.load(
            sample_dataframe,
            spreadsheet_id="invalid_id",
            range_name="Sheet1!A1",
            credential_file="fake_credential.json"
        )
        
        assert result is False
        captured = capsys.readouterr()
        assert "[Google Sheets Error]" in captured.out


class TestMultiDestinationDataLoader:
    """Tests for MultiDestinationDataLoader class."""
    
    @patch("utils.load.CsvDataLoader.load")
    @patch("utils.load.PostgreSQLDataLoader.load")
    @patch("utils.load.GoogleSheetsDataLoader.load")
    def test_load_to_all_success(self, mock_gsheet, mock_postgres, mock_csv, sample_dataframe):
        """Test loading to all destinations."""
        mock_csv.return_value = True
        mock_postgres.return_value = True
        mock_gsheet.return_value = True
        
        loader = MultiDestinationDataLoader()
        results = loader.load_to_all(sample_dataframe)
        
        assert results['csv'] is True
        assert results['postgresql'] is True
        assert results['google_sheets'] is True
        
        mock_csv.assert_called_once()
        mock_postgres.assert_called_once()
        mock_gsheet.assert_called_once()
    
    @patch("utils.load.CsvDataLoader.load")
    @patch("utils.load.PostgreSQLDataLoader.load")
    @patch("utils.load.GoogleSheetsDataLoader.load")
    def test_load_to_all_mixed_results(self, mock_gsheet, mock_postgres, mock_csv, sample_dataframe):
        """Test loading with mixed success/failure results."""
        mock_csv.return_value = True
        mock_postgres.return_value = False
        mock_gsheet.return_value = True
        
        loader = MultiDestinationDataLoader()
        results = loader.load_to_all(sample_dataframe)
        
        assert results['csv'] is True
        assert results['postgresql'] is False
        assert results['google_sheets'] is True


class TestLegacyFunctions:
    """Tests for legacy function wrappers."""
    
    @patch("utils.load.CsvDataLoader.load")
    def test_save_to_csv_legacy_wrapper(self, mock_load, sample_dataframe):
        """Test legacy save_to_csv function."""
        save_to_csv(sample_dataframe, filename="test.csv")
        mock_load.assert_called_once_with(sample_dataframe, filename="test.csv")
    
    @patch("utils.load.PostgreSQLDataLoader.load")
    def test_save_to_postgresql_legacy_wrapper(self, mock_load, sample_dataframe):
        """Test legacy save_to_postgresql function."""
        save_to_postgresql(
            sample_dataframe,
            db_name="test_db",
            user="user",
            password="password"
        )
        mock_load.assert_called_once()
    
    @patch("utils.load.GoogleSheetsDataLoader.load")
    def test_save_to_google_spreadsheet_legacy_wrapper(self, mock_load, sample_dataframe):
        """Test legacy save_to_google_spreadsheet function."""
        save_to_google_spreadsheet(
            sample_dataframe,
            spreadsheet_id="fake_id",
            range_name="Sheet1!A1"
        )
        mock_load.assert_called_once()
    
    @patch("utils.load.MultiDestinationDataLoader.load_to_all")
    def test_load_data_legacy_wrapper(self, mock_load_to_all, sample_dataframe):
        """Test legacy load_data function."""
        load_data(sample_dataframe)
        mock_load_to_all.assert_called_once()
