"""
Main ETL Pipeline module implementing SOLID principles.
This module orchestrates the Extract, Transform, and Load operations.
"""

import pandas as pd
from utils.extract import HttpContentFetcher, RegexTextExtractor, FashionProductParser, FashionDataExtractor
from utils.transform import FashionDataTransformer
from utils.load import MultiDestinationDataLoader


class ETLPipeline:
    """Main ETL Pipeline class following Single Responsibility Principle."""
    
    def __init__(self):
        # Initialize components following Dependency Injection
        self.content_fetcher = HttpContentFetcher()
        self.text_extractor = RegexTextExtractor()
        self.product_parser = FashionProductParser(self.text_extractor)
        self.data_extractor = FashionDataExtractor(self.content_fetcher, self.product_parser)
        self.data_transformer = FashionDataTransformer()
        self.data_loader = MultiDestinationDataLoader()
    
    def extract_data(self, total_pages: int = 50) -> pd.DataFrame:
        """Extract data from the source."""
        print("Starting data extraction process...")
        extracted_data = self.data_extractor.extract(total_pages=total_pages)
        
        if not extracted_data:
            print("No data was successfully extracted. Process stopped.")
            return pd.DataFrame()
        
        df_raw = pd.DataFrame(extracted_data)
        print(f"Extraction completed. Number of records: {len(df_raw)}")
        return df_raw
    
    def transform_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Transform raw data into cleaned format."""
        if df_raw.empty:
            return df_raw
        
        print("\n=======Data Information Before Transformation:=======")
        print(df_raw.info())
        print("\n=======Data Head Before Transformation:=======")
        print(df_raw.head())
        
        print("\nStarting data transformation process...")
        df_cleaned = self.data_transformer.transform(df_raw)
        print(f"Transformation completed. Number of records after cleaning: {len(df_cleaned)}")
        
        if not df_cleaned.empty:
            print("\n=======Data Information After Transformation:=======")
            print(df_cleaned.info())
            print("\n=======Data Head After Transformation:=======")
            print(df_cleaned.head())
        
        return df_cleaned
    
    def load_data(self, df_cleaned: pd.DataFrame) -> None:
        """Load data to storage destinations."""
        if df_cleaned.empty:
            print("No data to load.")
            return
        
        print("\nStarting data loading process to storage (CSV, PostgreSQL, Google Sheets)...")
        results = self.data_loader.load_to_all(df_cleaned)
        
        # Report results
        success_count = sum(results.values())
        total_destinations = len(results)
        
        print(f"Loading completed. {success_count}/{total_destinations} destinations successful.")
        
        for destination, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {destination}")
    
    def run(self, total_pages: int = 50) -> None:
        """Run the complete ETL pipeline."""
        try:
            # Extract
            df_raw = self.extract_data(total_pages)
            
            # Transform
            df_cleaned = self.transform_data(df_raw)
            
            # Load
            self.load_data(df_cleaned)
            
            print("\nETL process completed successfully.")
            
        except Exception as e:
            print(f"Error in main ETL process: {e}")


def main():
    """Main function to run the ETL pipeline."""
    pipeline = ETLPipeline()
    pipeline.run(total_pages=50)


if __name__ == '__main__':
    main()
