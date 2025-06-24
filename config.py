import os
from pathlib import Path

# Base directory - now using proper Path conversion
BASE_DIR = Path(__file__).parent.resolve()

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