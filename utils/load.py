"""
Data loading module implementing SOLID principles.
Contains concrete implementations for various data storage destinations.
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

from .interfaces import DataLoaderInterface
from .config import (
    DATABASE_CONFIG, 
    GOOGLE_SHEETS_CONFIG, 
    FILE_CONFIG,
    get_database_config
)

# Load environment variables
load_dotenv()


class CsvDataLoader(DataLoaderInterface):
    """Concrete implementation for CSV file loading."""
    
    def load(self, data: pd.DataFrame, **kwargs) -> bool:
        """Save DataFrame to CSV file."""
        filename = kwargs.get('filename', FILE_CONFIG['default_csv_filename'])
        try:
            data.to_csv(filename, index=False)
            print(f"[Flatfile-.CSV] Data successfully saved to {filename}")
            return True
        except Exception as e:
            print(f"[CSV Error] Failed to save data to CSV: {e}")
            return False


class PostgreSQLDataLoader(DataLoaderInterface):
    """Concrete implementation for PostgreSQL database loading."""
    
    def __init__(self):
        self.default_config = DATABASE_CONFIG
    
    def load(self, data: pd.DataFrame, **kwargs) -> bool:
        """Save DataFrame to PostgreSQL database."""
        db_name = kwargs.get('db_name')
        user = kwargs.get('user')
        password = kwargs.get('password')
        host = kwargs.get('host', self.default_config['default_host'])
        port = kwargs.get('port', self.default_config['default_port'])
        table_name = kwargs.get('table_name', self.default_config['default_table'])
        
        try:
            data_for_sql = data.copy()
            data_for_sql.columns = [col.lower() for col in data_for_sql.columns]
            
            engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')
            data_for_sql.to_sql(table_name, engine, index=False, if_exists='append')
            print(f"[PostgreSQL] Data successfully saved to table {table_name}.")
            return True
        except Exception as e:
            print(f"[PostgreSQL Error] Failed to save to PostgreSQL: {e}")
            return False


class GoogleSheetsDataLoader(DataLoaderInterface):
    """Concrete implementation for Google Sheets loading."""
    
    def __init__(self):
        self.scopes = GOOGLE_SHEETS_CONFIG['scopes']
    
    def load(self, data: pd.DataFrame, **kwargs) -> bool:
        """Save DataFrame to Google Spreadsheet."""
        spreadsheet_id = kwargs.get('spreadsheet_id')
        range_name = kwargs.get('range_name')
        credential_file = kwargs.get('credential_file', GOOGLE_SHEETS_CONFIG['default_credentials_file'])
        
        try:
            creds = Credentials.from_service_account_file(credential_file, scopes=self.scopes)
            service = build('sheets', 'v4', credentials=creds)

            # Clear existing data
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name,
            ).execute()

            # Format data
            values = [data.columns.tolist()] + data.values.tolist()
            body = {'values': values}

            # Update spreadsheet
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()

            print(f"[Google Sheets] Data successfully saved to Spreadsheet (Fashion Data Processing).")
            return True
        except Exception as e:
            print(f"[Google Sheets Error] Failed to save to Google Sheets: {e}")
            return False


class MultiDestinationDataLoader:
    """Orchestrates loading to multiple destinations."""
    
    def __init__(self):
        self.csv_loader = CsvDataLoader()
        self.postgres_loader = PostgreSQLDataLoader()
        self.sheets_loader = GoogleSheetsDataLoader()
    
    def load_to_all(
        self,
        data: pd.DataFrame,
        filename_csv: Optional[str] = None,
        db_config: Optional[Dict[str, Any]] = None,
        sheets_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Load data to all storage destinations."""
        
        # Use default filename if not provided
        if filename_csv is None:
            filename_csv = FILE_CONFIG['default_csv_filename']
        
        # Use centralized database configuration function
        default_db_config = get_database_config()
        
        default_sheets_config = {
            'spreadsheet_id': GOOGLE_SHEETS_CONFIG['default_spreadsheet_id'],
            'range_name': GOOGLE_SHEETS_CONFIG['default_range']
        }
        
        # Merge with user provided configs
        db_config = {**default_db_config, **(db_config or {})}
        sheets_config = {**default_sheets_config, **(sheets_config or {})}
        
        # Load to all destinations
        results = {}
        results['csv'] = self.csv_loader.load(data, filename=filename_csv)
        results['postgresql'] = self.postgres_loader.load(data, **db_config)
        results['google_sheets'] = self.sheets_loader.load(data, **sheets_config)
        
        return results


# Legacy function wrappers for backward compatibility
def save_to_csv(df: pd.DataFrame, filename: str = 'fashion_data.csv') -> None:
    """Legacy wrapper for CsvDataLoader."""
    loader = CsvDataLoader()
    loader.load(df, filename=filename)


def save_to_postgresql(
    df: pd.DataFrame,
    db_name: str,
    user: str,
    password: str,
    host: str = 'localhost',
    port: int = 5432,
    table_name: str = 'fashion_products'
) -> None:
    """Legacy wrapper for PostgreSQLDataLoader."""
    loader = PostgreSQLDataLoader()
    loader.load(
        df,
        db_name=db_name,
        user=user,
        password=password,
        host=host,
        port=port,
        table_name=table_name
    )


def save_to_google_spreadsheet(
    df: pd.DataFrame,
    spreadsheet_id: str,
    range_name: str,
    credential_file: str = 'client_secret.json'
) -> None:
    """Legacy wrapper for GoogleSheetsDataLoader."""
    loader = GoogleSheetsDataLoader()
    loader.load(
        df,
        spreadsheet_id=spreadsheet_id,
        range_name=range_name,
        credential_file=credential_file
    )

def load_data(
    df: pd.DataFrame,
    filename_csv: str = 'fashion_data.csv',
    db_name: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    table_name: str = 'fashion_products',
    spreadsheet_id: str = '1MDLjCAZ2eMy-FxvBpDSJfNEkTOKOVoHORcrlyT8Vu-s',
    range_name: str = 'Sheet1!A1'
) -> None:
    """Legacy wrapper for MultiDestinationDataLoader."""
    loader = MultiDestinationDataLoader()
    
    # Prepare configurations
    db_config = None
    if any([db_name, user, password, host, port]):
        db_config = {}
        if db_name: db_config['db_name'] = db_name
        if user: db_config['user'] = user
        if password: db_config['password'] = password
        if host: db_config['host'] = host
        if port: db_config['port'] = port
        if table_name != 'fashion_products': db_config['table_name'] = table_name
    
    sheets_config = None
    if spreadsheet_id != GOOGLE_SHEETS_CONFIG['default_spreadsheet_id'] or range_name != GOOGLE_SHEETS_CONFIG['default_range']:
        sheets_config = {
            'spreadsheet_id': spreadsheet_id,
            'range_name': range_name
        }
    
    loader.load_to_all(df, filename_csv, db_config, sheets_config)
