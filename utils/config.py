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
    "default_spreadsheet_id": "1MDLjCAZ2eMy-FxvBpDSJfNEkTOKOVoHORcrlyT8Vu-s",
    "default_range": "Sheet1!A1",
    "default_credentials_file": "google-sheets-api.json"
}

# Transformation Configuration
TRANSFORMATION_CONFIG: Dict[str, Any] = {
    "usd_to_idr_rate": 16000,
    "price_decimal_places": 1
}

# ETL Pipeline Configuration
ETL_CONFIG: Dict[str, Any] = {
    "default_pages": 50,
    "default_delay": 2,
    "max_retries": 3,
    "timeout_seconds": 30
}

# HTTP Request Configuration
HTTP_CONFIG: Dict[str, Any] = {
    "timeout": 30,
    "retries": 3,
    "backoff_factor": 0.3,
    "status_forcelist": [500, 502, 503, 504]
}

# Logging Configuration  
LOGGING_CONFIG: Dict[str, Any] = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "log_to_file": False,
    "log_file_path": "logs/etl_pipeline.log"
}

# Application Configuration
APP_CONFIG: Dict[str, Any] = {
    "app_name": "ETL Pipeline Fashion Data",
    "version": "1.0.0",
    "author": "Faris Munir Mahdi",
    "description": "Membangun ETL Pipeline Sederhana",
    "created_date": "2025-06-29"
}

# Docker Configuration
DOCKER_CONFIG: Dict[str, str] = {
    "postgres_image": "postgres:15",
    "postgres_container_name": "postgres",
    "postgres_port": "5432:5432",
    "postgres_volume_data": "./postgres_data:/var/lib/postgresql/data",
    "postgres_volume_init": "./migrations/init_database.sql:/docker-entrypoint-initdb.d/init_database.sql",
    "healthcheck_test": "pg_isready -U postgres",
    "healthcheck_interval": "30s",
    "healthcheck_timeout": "10s",
    "healthcheck_retries": "5"
}

# Makefile Commands Configuration
MAKEFILE_CONFIG: Dict[str, str] = {
    "migrate_command": "docker compose up -d",
    "app_command": "python main.py", 
    "test_command": "python -m pytest tests"
}

# Test Configuration
TEST_CONFIG: Dict[str, Any] = {
    "test_data_sample_size": 10,
    "test_timeout": 30,
    "test_coverage_min": 80,
    "test_files_pattern": "test_*.py"
}

# Error Messages Configuration
ERROR_MESSAGES: Dict[str, str] = {
    "extraction_failed": "Failed to extract data from source",
    "transformation_failed": "Failed to transform data", 
    "loading_failed": "Failed to load data to destination",
    "connection_failed": "Failed to establish connection",
    "invalid_data": "Invalid or corrupted data detected",
    "file_not_found": "Required file not found",
    "credentials_invalid": "Invalid credentials provided"
}

# Success Messages Configuration  
SUCCESS_MESSAGES: Dict[str, str] = {
    "extraction_complete": "Data extraction completed successfully",
    "transformation_complete": "Data transformation completed successfully",
    "loading_complete": "Data loading completed successfully", 
    "connection_established": "Connection established successfully",
    "file_saved": "File saved successfully",
    "pipeline_complete": "ETL pipeline completed successfully"
}

# File Path Configuration
PATHS_CONFIG: Dict[str, str] = {
    "data_dir": "data/",
    "logs_dir": "logs/", 
    "migrations_dir": "migrations/",
    "tests_dir": "tests/",
    "utils_dir": "utils/",
    "screenshots_dir": "screenshoot/",
    "guide_dir": "guide/",
    "postgres_data_dir": "postgres_data/"
}

# Git Configuration
GIT_CONFIG: Dict[str, Any] = {
    "repo_url": "https://github.com/maxwellmassie/submission-prada.git",
    "gitignore_patterns": [
        ".env", "client_secret.json", "*.pyc", "__pycache__/",
        ".venv/", "venv/", ".mypy_cache/", ".pytest_cache/"
    ]
}

# Environment Variables Configuration
ENV_VARS: Dict[str, str] = {
    "postgres_user": "POSTGRES_USER",
    "postgres_password": "POSTGRES_PASSWORD", 
    "postgres_db": "POSTGRES_DB",
    "postgres_host": "POSTGRES_HOST",
    "postgres_port": "POSTGRES_PORT"
}

# Dependencies Configuration (dari requirements.txt)
DEPENDENCIES_CONFIG: Dict[str, str] = {
    "python_crontab": "~=3.2",
    "sqlalchemy": "~=2.0",
    "psycopg2_binary": "~=2.9",
    "pandas": "~=2.2",
    "requests": "~=2.32",
    "beautifulsoup4": "~=4.12",
    "google_auth": "~=2.36",
    "google_api_python_client": "~=2.152",
    "python_dotenv": "~=1.0",
    "pytest_cov": "~=6.0"
}

# Package Installation Configuration
INSTALL_CONFIG: Dict[str, Any] = {
    "pip_upgrade": "pip install --upgrade pip",
    "install_requirements": "pip install -r requirements.txt",
    "install_dev_requirements": "pip install -r requirements-dev.txt",
    "virtual_env_create": "python -m venv .env",
    "virtual_env_activate_windows": ".env\\Scripts\\activate",
    "virtual_env_activate_linux": "source .env/bin/activate"
}

# Validation Configuration
VALIDATION_CONFIG: Dict[str, Any] = {
    "required_files": [
        "main.py", "requirements.txt", "docker-compose.yml",
        "google-sheets-api.json", "fashion_data.csv"
    ],
    "required_directories": [
        "utils/", "tests/", "migrations/", "postgres_data/", 
        "screenshoot/", "guide/"
    ],
    "file_extensions": {
        "python": [".py"],
        "data": [".csv", ".json"],
        "config": [".yml", ".yaml", ".env", ".ini"],
        "docs": [".md", ".txt", ".rst"]
    }
}

# Data Quality Configuration
DATA_QUALITY_CONFIG: Dict[str, Any] = {
    "min_rows_threshold": 1,
    "max_null_percentage": 50.0,
    "required_columns": ["Title", "Price", "Rating", "Colors", "Size", "Gender"],
    "data_types": {
        "Title": "object",
        "Price": "float64", 
        "Rating": "float64",
        "Colors": "int64",
        "Size": "object",
        "Gender": "object"
    }
}

# Performance Configuration
PERFORMANCE_CONFIG: Dict[str, Any] = {
    "chunk_size": 1000,
    "batch_size": 100,
    "connection_pool_size": 5,
    "max_workers": 4,
    "memory_limit_mb": 512,
    "timeout_requests": 30
}
