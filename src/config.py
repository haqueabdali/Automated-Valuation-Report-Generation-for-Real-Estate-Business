import os
from pathlib import Path
from typing import Dict, Any

# Base directory - now using proper Path conversion
BASE_DIR = Path(__file__).parent.resolve()

# Scrapping configuration
SCRAPING_CONFIG = {
    'REQUEST_DELAY': 1.5,  # Seconds between requests
    'RETRY_ATTEMPTS': 3,
    'USER_AGENT_ROTATION': True
}

# Web Scraping Configuration
SCRAPING_SETTINGS = {
    'delay': 2.5,  # Seconds between requests
    'timeout': 10,  # Request timeout
    'retries': 3,  # Max retries per request
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    ]
}

# Path configurations using proper path joining
DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "outputs" / "reports"
TEMPLATE_DIR = BASE_DIR / "templates"
REPORT_TEMPLATE = TEMPLATE_DIR / "report_template.docx"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Report template file
REPORT_TEMPLATE = TEMPLATE_DIR / "report_template.docx"

# Data files
PROPERTY_DATA_FILE = DATA_DIR / "property_data.csv"
COMPARABLE_SALES_FILE = DATA_DIR / "comparable_sales.csv"

# Valuation parameters
VALUATION_METHODS = ["sales_comparison", "income_approach", "cost_approach"]
DEFAULT_METHOD = "sales_comparison"

# Report styling
COMPANY_LOGO = None  # Path to logo if available
COMPANY_NAME = "Real Estate Valuation Inc."


# Proxy Configuration
PROXY_SETTINGS = {
    'enabled': True,  # Set to False to disable proxies
    'refresh_interval': 3600,  # 1 hour in seconds
    'max_proxies': 20,
    'test_url': 'http://httpbin.org/ip',  # URL to test proxies
    'sources': [
        'geonode',
        'proxyscrape',
        'freeproxy'
    ],
    # For authenticated proxies (if you upgrade to paid later)
    'auth': {
        'username': os.getenv('PROXY_USER', ''),
        'password': os.getenv('PROXY_PASS', '')
    }
}
