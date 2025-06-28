import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Project root directory
BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / 'data'
TEMPLATES_DIR = BASE_DIR / 'templates'
OUTPUT_DIR = BASE_DIR / 'outputs'
LOGS_DIR = BASE_DIR / 'logs'
REPORTS_DIR = OUTPUT_DIR / 'reports'

# Directory structure configuration
DIR_CONFIG = {
    'DATA': DATA_DIR,
    'TEMPLATES': TEMPLATES_DIR,
    'OUTPUT': OUTPUT_DIR,
    'LOGS': LOGS_DIR,
    'REPORTS': REPORTS_DIR
}

# Create all required directories
for dir_path in DIR_CONFIG.values():
    dir_path.mkdir(parents=True, exist_ok=True)

# File paths
PROPERTY_DATA_FILE = DATA_DIR / "property_data.csv"
COMPARABLE_SALES_FILE = DATA_DIR / "comparable_sales.csv"
LOG_FILE = LOGS_DIR / "valuation_system.log"
REPORT_TEMPLATE = TEMPLATES_DIR / "report_template.html"
COMPANY_LOGO = TEMPLATES_DIR / "company_logo.png"

# Initialize default data files if missing
if not PROPERTY_DATA_FILE.exists():
    with open(PROPERTY_DATA_FILE, 'w') as f:
        f.write("""id,address,city,state,zip_code,property_type,bedrooms,bathrooms,sqft,lot_size,year_built,price
1,123 Main St,Anytown,CA,12345,Single Family,3,2.5,1800,0.25,1995,750000
2,456 Oak Ave,Somewhere,CA,54321,Condo,2,2,1200,0.1,2010,650000""")

if not COMPARABLE_SALES_FILE.exists():
    with open(COMPARABLE_SALES_FILE, 'w') as f:
        f.write("""id,address,property_type,bedrooms,bathrooms,sqft,lot_size,year_built,sale_price,sale_date,distance_miles
101,124 Main St,Single Family,3,2,1750,0.23,1998,725000,2023-01-15,0.1
102,125 Main St,Single Family,4,2.5,2000,0.3,1997,800000,2023-02-20,0.2""")

# Report configuration
REPORT_TEMPLATE = TEMPLATES_DIR / 'report_template.docx'  
COMPANY_NAME = "Real Estate Valuation Inc."

# Valuation methods
VALUATION_METHODS = [
    "sales_comparison",
    "income_approach", 
    "cost_approach",
    "hybrid"
]
DEFAULT_METHOD = "sales_comparison"

# Web scraping configuration
SCRAPING_SETTINGS = {
    'delay': 2.5,  # seconds between requests
    'timeout': 10,  # request timeout in seconds
    'retries': 3,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    ]
}

# Model configuration
MODEL_CONFIG = {
    'default_path': BASE_DIR / 'models' / 'trained_model.pkl',
    'fallback_params': {
        'n_estimators': 150,
        'max_depth': 10,
        'min_samples_split': 5,
        'random_state': 42
    }
}

# Logging configuration
LOG_LEVEL = 'INFO'

# API configuration (if using external services)
API_KEYS = {
    'ZILLOW_API_KEY': os.getenv('ZILLOW_API_KEY', ''),
    'REDFIN_API_KEY': os.getenv('REDFIN_API_KEY', ''),
    'MAX_CALLS_PER_MINUTE': 10
}

# Data processing configuration
DATA_FILES = {
    "property_data": PROPERTY_DATA_FILE,
    "comparable_sales": COMPARABLE_SALES_FILE
}

# Report generation configuration
REPORT_CONFIG = {
    "output_dir": REPORTS_DIR,
    "image_formats": ["png", "svg"],
    "default_format": "pdf"
}

class Config:
    """Configuration class for easy access to settings."""
    def __init__(self):
        self.BASE_DIR = BASE_DIR
        self.DATA_DIR = DATA_DIR
        self.LOGS_DIR = LOGS_DIR
        self.REPORTS_DIR = REPORTS_DIR
        self.TEMPLATES_DIR = TEMPLATES_DIR
        self.PROPERTY_DATA_FILE = PROPERTY_DATA_FILE
        self.COMPARABLE_SALES_FILE = COMPARABLE_SALES_FILE
        self.LOG_FILE = LOG_FILE
        self.REPORT_TEMPLATE = REPORT_TEMPLATE
        self.COMPANY_NAME = COMPANY_NAME
        self.COMPANY_LOGO = COMPANY_LOGO
        self.DEFAULT_METHOD = DEFAULT_METHOD
        self.VALUATION_METHODS = VALUATION_METHODS
        self.LOG_LEVEL = LOG_LEVEL
        self.DATA_FILES = DATA_FILES
        self.REPORT_CONFIG = REPORT_CONFIG
        self.API_KEYS = API_KEYS
        self.SCRAPING_SETTINGS = SCRAPING_SETTINGS
        self.MODEL_CONFIG = MODEL_CONFIG

# Create a config instance for direct import
config = Config()

def validate_config() -> bool:
    """Validate that all required configuration is properly set up."""
    try:
        required_dirs = [DATA_DIR, LOGS_DIR, REPORTS_DIR, TEMPLATES_DIR]
        required_files = [REPORT_TEMPLATE]
        
        for directory in required_dirs:
            if not directory.exists():
                directory.mkdir(parents=True)
                
        for file in required_files:
            if not file.exists():
                raise FileNotFoundError(f"Required file not found: {file}")
                
        return True
    except Exception as e:
        print(f"Configuration validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Current configuration:")
    print(f"Base directory: {BASE_DIR}")
    print(f"Property data file: {PROPERTY_DATA_FILE}")
    print(f"Comparable sales file: {COMPARABLE_SALES_FILE}")
    print(f"Valuation methods: {VALUATION_METHODS}")
    
    if validate_config():
        print("Configuration is valid")
    else:
        print("Configuration validation failed")