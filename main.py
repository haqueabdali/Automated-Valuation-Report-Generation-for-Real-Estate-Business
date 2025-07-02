import argparse
import sys
import logging
from pathlib import Path
import matplotlib
from src.web_scraping.scrapers import ZillowScraper
matplotlib.use('Agg')  # Set non-interactive backend
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))
# For imports from config.py (assuming config.py is in src/)
# Local imports
from src.config import (
    DEFAULT_METHOD,
    VALUATION_METHODS,
    COMPANY_NAME,
    REPORT_TEMPLATE,
    LOG_FILE,
    LOG_LEVEL,
    PROPERTY_DATA_FILE,
    COMPARABLE_SALES_FILE
)
from src.data_processing.data_processor import DataProcessor
from src.valuation_calculator import ValuationCalculator
from src.report_generation.report_generator import ReportGenerator
from src.web_scraping.scraper_manager import property_scraper
from src.report_generation.docx_generation import generate_report
# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Configure argument parser with enhanced validation"""
    parser = argparse.ArgumentParser(
        description='Automated Real Estate Valuation Report Generator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input methods (mutually exclusive and required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--csv', 
        type=str,
        help='Path to CSV file containing property data'
    )
    input_group.add_argument(
        '--urls', 
        nargs='+',
        help='List of property URLs to scrape data from'
    )
    input_group.add_argument(
        '--property-id', 
        type=int,
        help='Database property ID to lookup'
    )
    
    # Valuation parameters
    parser.add_argument(
        '--method', 
        choices=VALUATION_METHODS, 
        default=DEFAULT_METHOD,
        help='Valuation methodology to apply'
    )
    parser.add_argument(
        '--all-methods', 
        action='store_true',
        help='Execute all valuation methods and compare results'
    )
    
    return parser.parse_args()

def load_property_data(args, data_processor):
    """Handle data loading from different sources with validation"""
    try:
        if args.csv:
            logger.info(f"Loading data from CSV: {args.csv}")
            if not data_processor.load_data_from_csv(args.csv):
                raise ValueError("Failed to load CSV data")
            return data_processor.get_property_details(args.property_id)
            
        elif args.urls:
            logger.info(f"Scraping data from URLs: {args.urls}")
            if not data_processor.scrape_property_data(args.urls):
                raise ValueError("Failed to scrape property data")
            return data_processor.get_scraped_property_details()
            
        else:
            logger.info(f"Loading property ID: {args.property_id}")
            if not data_processor.load_data(PROPERTY_DATA_FILE, COMPARABLE_SALES_FILE):
                raise ValueError("Failed to load default data")
            return data_processor.get_property_details(args.property_id)
            
    except Exception as e:
        logger.error(f"Data loading failed: {str(e)}")
        raise

def calculate_valuations(args, property_details, calculator):
    """Execute valuation calculations with error handling"""
    try:
        if args.all_methods:
            logger.info("Running all valuation methods...")
            results = []
            for method in VALUATION_METHODS:
                logger.info(f"Calculating {method} valuation...")
                result = calculator.calculate_valuation(property_details, method)
                if result:
                    results.append(result)
            return sorted(results, key=lambda x: x.confidence, reverse=True)
        else:
            logger.info(f"Calculating valuation using {args.method} method...")
            return calculator.calculate_valuation(property_details, args.method)
    except Exception as e:
        logger.error(f"Valuation calculation failed: {str(e)}")
        raise

def main():
    
    zillow_url = input("Enter Zillow property URL: ")
    try:
        generate_report(zillow_url)
        print("Report generated successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    try:
        args = parse_arguments()
        logger.info("Initializing valuation system components")
        
        # Initialize system components
        data_processor = DataProcessor()
        valuation_calculator = ValuationCalculator(data_processor)
        report_generator = ReportGenerator(REPORT_TEMPLATE, COMPANY_NAME)
        
        # Data loading phase
        property_details = load_property_data(args, data_processor)
        if not property_details:
            error_msg = "No property found"
            if not args.urls:
                error_msg += f" with ID {args.property_id}"
            raise ValueError(error_msg)
        
        # Valuation calculation phase
        valuation_results = calculate_valuations(args, property_details, valuation_calculator)
        if not valuation_results:
            raise ValueError("No valid valuation results obtained")
        
        # Report generation phase
        
        data_source = "Web Scraping" if args.urls else ("CSV" if args.csv else "Database")
        report_path = report_generator.generate_report(
            property_details=property_details,
            valuation_results=valuation_results,
            data_source=data_source
        )
        
        logger.info(f"Successfully generated valuation report: {report_path}")
        return 0
        
    except argparse.ArgumentError as e:
        logger.error(f"Argument error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())