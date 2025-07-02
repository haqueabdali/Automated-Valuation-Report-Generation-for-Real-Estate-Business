# src/web_scraping/zillow_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time
import logging
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class ZillowScraper:
    def __init__(self, url):
        self.url = url
        self.ua = UserAgent()
        self.driver = None
        
    def initialize_driver(self):
        """Initialize Chrome WebDriver with options"""
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={self.ua.random}')
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def scrape(self):
        """Scrape property data from Zillow URL"""
        try:
            self.initialize_driver()
            self.driver.get(self.url)
            time.sleep(3)  # Wait for page to load
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract property details
            return {
                'address': self.get_address(soup),
                'price': self.get_price(soup),
                'bedrooms': self.get_bedrooms(soup),
                'bathrooms': self.get_bathrooms(soup),
                'sqft': self.get_sqft(soup),
                'lot_size': self.get_lot_size(soup),
                'year_built': self.get_year_built(soup)
            }
        except Exception as e:
            logger.error(f"Error scraping {self.url}: {str(e)}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_address(self, soup):
        element = soup.select_one('h1[data-testid="address"]')
        return element.text.strip() if element else "N/A"
    
    def get_price(self, soup):
        element = soup.select_one('span[data-testid="price"]')
        if element:
            price_text = element.text.strip().replace('$', '').replace(',', '')
            return float(price_text) if price_text.replace('.', '', 1).isdigit() else 0
        return 0
    
    def get_bedrooms(self, soup):
        element = soup.select_one('span[data-testid="bedrooms"]')
        if element:
            return int(element.text.split()[0]) if element.text.split()[0].isdigit() else 0
        return 0
    
    def get_bathrooms(self, soup):
        element = soup.select_one('span[data-testid="bathrooms"]')
        if element:
            return float(element.text.split()[0]) if element.text.split()[0].replace('.', '', 1).isdigit() else 0
        return 0
    
    def get_sqft(self, soup):
        element = soup.select_one('span[data-testid="floor-space"]')
        if element:
            sqft_text = element.text.split()[0].replace(',', '')
            return int(sqft_text) if sqft_text.isdigit() else 0
        return 0
    
    def get_lot_size(self, soup):
        # Look for lot size in various places
        text = str(soup)
        if 'acres' in text:
            match = re.search(r'(\d+\.?\d*)\s*acres?', text)
            return float(match.group(1)) if match else 0
        elif 'sqft' in text:
            match = re.search(r'(\d+,\d+|\d+)\s*sq\.?\s*ft\.?', text)
            if match:
                return float(match.group(1).replace(',', '')) / 43560  # Convert to acres
        return 0
    
    def get_year_built(self, soup):
        element = soup.find('span', string=re.compile(r'Built'))
        if element:
            year_text = re.search(r'\d{4}', element.text)
            return int(year_text.group()) if year_text else 0
        return 0