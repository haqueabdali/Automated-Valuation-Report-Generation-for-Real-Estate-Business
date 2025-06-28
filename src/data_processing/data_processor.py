import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
PROPERTY_DATA_FILE = "data/property_data.csv"
COMPARABLE_SALES_FILE = "data/comparable_sales.csv"
from src.config import PROPERTY_DATA_FILE, COMPARABLE_SALES_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self):
        """Initialize data processor with empty DataFrames"""
        self.property_data = pd.DataFrame()
        self.comparable_sales = pd.DataFrame()
        logger.info("DataProcessor initialized")

    def _validate_file(self, file_path: Union[str, Path]) -> bool:
        """Validate that a file exists and is readable"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {path}")
                return False
            if not path.is_file():
                logger.error(f"Path is not a file: {path}")
                return False
            if path.stat().st_size == 0:
                logger.error(f"File is empty: {path}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error validating file {path}: {str(e)}")
            return False

    def load_data_from_csv(self, csv_path: Union[str, Path]) -> bool:
        """Load property data from CSV file with robust error handling"""
        try:
            # Define the files to load
            data_files = {
                'property_data': PROPERTY_DATA_FILE,
                'comparable_sales': COMPARABLE_SALES_FILE
            }
            
            # Validate files before loading
            if not all(self._validate_file(f) for f in data_files.values()):
                return False
            
            # Load data
            self.property_data = pd.read_csv(PROPERTY_DATA_FILE)
            self.comparable_sales = pd.read_csv(COMPARABLE_SALES_FILE)
            
            # Clean and validate data
            self._clean_data()
            
            logger.info("Successfully loaded all data")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False

    def scrape_property_data(self, urls: List[str]) -> bool:
        """Scrape property data from URLs with comprehensive error handling"""
        properties = []
        for url in urls:
            try:
                if 'zillow' in url:
                    scraped = scrape_zillow(url)
                    if scraped:
                        properties.append(map_to_model(scraped))
                elif 'redfin' in url:
                    scraped = scrape_redfin(url)
                    if scraped:
                        properties.append(map_to_model(scraped))
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        if properties:
            self.property_data = pd.DataFrame(properties)
            logger.info(f"Successfully scraped {len(properties)} properties")
            return True
        
        logger.error("No valid properties scraped from URLs")
        return False

    def load_data(self,  property_data_file: Union[str, Path], comparable_sales_file: Union[str, Path]) -> bool:
        """Load both property and comparable sales data with validation"""
        try:
            # Validate files before loading
            if not all(self._validate_file(f) for f in [PROPERTY_DATA_FILE, COMPARABLE_SALES_FILE]):
                return False
            
            # Load data
            self.property_data = pd.read_csv(PROPERTY_DATA_FILE)
            self.comparable_sales = pd.read_csv(COMPARABLE_SALES_FILE)
            
            # Clean and validate data
            self._clean_data()
            
            logger.info("Successfully loaded all data")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False

    def _clean_data(self):
        """Clean and standardize loaded data"""
        # Clean property data
        if 'id' in self.property_data.columns:
            self.property_data['id'] = self.property_data['id'].astype(str).str.strip()
        
        # Clean comparable sales
        numeric_cols = ['bedrooms', 'bathrooms', 'sqft', 'lot_size', 'year_built']
        for col in numeric_cols:
            if col in self.comparable_sales.columns:
                self.comparable_sales[col] = pd.to_numeric(self.comparable_sales[col], errors='coerce')

    def get_scraped_property_details(self) -> Optional[Dict]:
        """Get details of the first scraped property"""
        if not self.property_data.empty:
            return self.property_data.iloc[0].to_dict()
        logger.warning("No property data available")
        return None

    def get_property_details(self, property_id: Union[int, str]) -> Optional[Dict]:
        """Get details for a specific property with robust error handling"""
        try:
            if self.property_data.empty and not self.load_data():
                logger.error("No property data available")
                return None
            
            # Standardize ID format
            property_id = str(property_id).strip()
            if 'id' not in self.property_data.columns:
                logger.error("'id' column not found in property data")
                return None
            
            # Find matching property
            matches = self.property_data[
                self.property_data['id'].astype(str).str.strip() == property_id
            ]
            
            if matches.empty:
                logger.warning(f"No property found with ID: {property_id}")
                return None
                
            return matches.iloc[0].to_dict()
            
        except Exception as e:
            logger.error(f"Error getting property details: {str(e)}")
            return None

    def get_comparable_sales(self, property_id: Union[int, str], 
                           radius_miles: float = 5, 
                           max_comparables: int = 5) -> Optional[List[Dict]]:
        """Get comparable sales for a property with comprehensive validation"""
        try:
            # Get subject property
            subject = self.get_property_details(property_id)
            if not subject:
                return None
            
            # Validate comparable sales data
            if self.comparable_sales.empty and not self.load_data():
                return None
            
            # Filter comparables (enhanced logic)
            comparables = self.comparable_sales.copy()
            
            # Property type filter
            if 'property_type' in subject:
                comparables = comparables[
                    comparables['property_type'] == subject['property_type']
                ]
            
            # Bedrooms filter (±1)
            if 'bedrooms' in subject:
                comparables = comparables[
                    comparables['bedrooms'].between(
                        max(1, subject['bedrooms'] - 1),
                        subject['bedrooms'] + 1
                    )
                ]
            
            # Bathrooms filter (±0.5)
            if 'bathrooms' in subject:
                comparables = comparables[
                    comparables['bathrooms'].between(
                        max(1, subject['bathrooms'] - 0.5),
                        subject['bathrooms'] + 0.5
                    )
                ]
            
            # Square footage filter (±20%)
            if 'sqft' in subject:
                comparables = comparables[
                    comparables['sqft'].between(
                        subject['sqft'] * 0.8,
                        subject['sqft'] * 1.2
                    )
                ]
            
            # Limit results
            comparables = comparables.head(max_comparables)
            
            if comparables.empty:
                logger.warning("No comparable sales found matching criteria")
                return None
                
            return comparables.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting comparable sales: {str(e)}")
            return None