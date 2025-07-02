# src/web_scraping/scraper_manager.py
from .zillow_scraper import ZillowScraper
from .redfin_scraper import RedfinScraper  # If you have a Redfin scraper
import logging

logger = logging.getLogger(__name__)

def property_scraper(url):
    """Route to appropriate scraper based on URL domain"""
    try:
        if 'zillow.com' in url:
            scraper = ZillowScraper(url)
            return scraper.scrape()
        elif 'redfin.com' in url:
            scraper = RedfinScraper(url)
            return scraper.scrape()
        else:
            logger.warning(f"Unsupported website: {url}")
            return None
    except Exception as e:
        logger.error(f"Scraping failed for {url}: {str(e)}")
        return None