import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import PROXY_SETTINGS


# Implement proxy rotation
from proxy_requests import ProxyRequests
from .proxies import get_proxy
import logging
logger = logging.getLogger(__name__)

# def scrape_zillow(url):
#     ua = UserAgent()
#     headers = {'User-Agent': ua.random}

def get_proxy():
    if PROXY_SETTINGS['enabled']:
        return PROXY_SETTINGS['list'][0]  # Simple rotation
    return None

def get_random_user_agent():
    return random.choice(SCRAPING_SETTINGS['user_agents'])

def get_request_settings():
    """Generate settings for requests"""
    settings = {
        'headers': {'User-Agent': get_random_user_agent()},
        'timeout': SCRAPING_SETTINGS['timeout']
    }
    
    if PROXY_SETTINGS['enabled']:
        from proxies import get_proxy  # Import here to avoid circular imports
        proxy = get_proxy()
        if proxy:
            settings['proxies'] = proxy
    
    return settings

def safe_scrape(url, max_retries=3):
    headers = {'User-Agent': 'Mozilla/5.0'}  # Basic headers
    for _ in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception:
            time.sleep(random.uniform(1, 3))
    return None

def scrape_zillow(url):
        session = ProxyRequests(url)
        session.get()
        soup = BeautifulSoup(session.get_raw(), 'html.parser')
    
        try:
            proxy = get_proxy()
            response = requests.get(url, proxies={"http": proxy, "https": proxy})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        
            return {
                'address': soup.select_one('h1[data-testid="address"]').text.strip(),
                'price': float(soup.select_one('span[data-testid="price"]').text.strip().replace('$', '').replace(',', '')),
                'bedrooms': int(soup.select_one('span[data-testid="bedrooms"]').text.split()[0]),
                'bathrooms': float(soup.select_one('span[data-testid="bathrooms"]').text.split()[0]),
                'sqft': int(soup.select_one('span[data-testid="floor-space"]').text.split()[0].replace(',', '')),
                'lot_size': parse_lot_size(soup)
            }

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
        
        return None

def scrape_redfin(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JS rendering
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        return {
            'address': soup.select_one('.street-address').text.strip(),
            'price': float(soup.select_one('.home-main-value').text.replace('$', '').replace(',', '')),
            'bedrooms': int(soup.select_one('span:contains("Beds") + span').text),
            'bathrooms': float(soup.select_one('span:contains("Baths") + span').text),
            'sqft': int(soup.select_one('span:contains("Sq. Ft.") + span').text.replace(',', '')),
            'lot_size': parse_lot_size(soup)
        }
    except Exception as e:
        print(f"Error scraping Redfin: {e}")
        return None
    finally:
        driver.quit()

def parse_lot_size(soup):
    # Add parsing logic for different lot size formats
    return 0.0  # Default value