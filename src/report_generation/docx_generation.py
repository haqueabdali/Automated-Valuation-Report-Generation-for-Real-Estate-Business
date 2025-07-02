from ..web_scraping.scraper_manager import property_scraper

def generate_report(property_url: str):
    # 1. Scrape data
    scraped_data = property_scraper.get_property_data(property_url)
    
    if not scraped_data:
        raise ValueError("Failed to scrape property data")
    
    # 2. Process data (your existing logic)
    processed_data = {
        'address': scraped_data['address'],
        'valuation': scraped_data.get('zestimate', 'N/A'),
        # ... map other fields
    }