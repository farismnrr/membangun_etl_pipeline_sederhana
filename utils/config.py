"""
Configuration module for the ETL pipeline.
Contains all constants and configuration settings.
"""

from typing import Dict, Any
import os

# HTTP Configuration
HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

# URL Configuration
BASE_URL: str = "https://fashion-studio.dicoding.dev/"

# Data Extraction Patterns
EXTRACTION_PATTERNS: Dict[str, str] = {
    "rating": r"Rating:\s*(⭐\s*\d+(?:\.\d+)?)",
    "colors": r"(\d+)\s*Colors",
    "size": r"Size:\s*(\w+)",
    "gender": r"Gender:\s*(\w+)"
}

# Default Values
DEFAULT_VALUES: Dict[str, str] = {
    "title": "Unknown Title",
    "price": "Price Not Available",
    "rating": "Invalid Rating",
    "colors": "No Colors",
    "size": "Unknown",
    "gender": "Unknown"
}

# File Configuration
FILE_CONFIG: Dict[str, str] = {
    "default_csv_filename": "fashion_data.csv",
    "google_credentials_file": "google-sheets-api.json",
    "legacy_credentials_file": "client_secret.json"
}

# Database Configuration
DATABASE_CONFIG: Dict[str, Any] = {
    "default_host": "localhost",
    "default_port": 5432,
    "default_table": "fashion_products",
    "default_db_name": "fashion_db",
    "default_user": "postgres",
    "default_password": "postgres"
}

# Environment-based Database Configuration
def get_database_config() -> Dict[str, Any]:
    """Get database configuration from environment variables with fallbacks."""
    return {
        "db_name": os.getenv("POSTGRES_DB", DATABASE_CONFIG["default_db_name"]),
        "user": os.getenv("POSTGRES_USER", DATABASE_CONFIG["default_user"]),
        "password": os.getenv("POSTGRES_PASSWORD", DATABASE_CONFIG["default_password"]),
        "host": os.getenv("POSTGRES_HOST", DATABASE_CONFIG["default_host"]),
        "port": int(os.getenv("POSTGRES_PORT", str(DATABASE_CONFIG["default_port"]))),
        "table_name": DATABASE_CONFIG["default_table"]
    }

# Google Sheets Configuration
GOOGLE_SHEETS_CONFIG: Dict[str, Any] = {
    "scopes": ["https://www.googleapis.com/auth/spreadsheets"],
    "default_spreadsheet_id": "1bZOhgq65Tqkw-rIBBQTcHNMnGeW2tYQ7A-nMpXe-Lt0",
    "default_range": "Sheet1!A1",
    "default_credentials_file": "google-sheets-api.json"
}

# Transformation Configuration
TRANSFORMATION_CONFIG: Dict[str, Any] = {
    "usd_to_idr_rate": 16000,
    "price_decimal_places": 1
}