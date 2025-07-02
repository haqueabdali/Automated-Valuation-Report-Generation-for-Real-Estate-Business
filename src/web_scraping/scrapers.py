import requests
from bs4 import BeautifulSoup
import random
import time
from fake_useragent import UserAgent
import json
from typing import Dict, Optional

class ZillowScraper:
    def __init__(self):
        self.base_url = "https://www.zillow.com"
        self.session = requests.Session()
        self.user_agent = UserAgent()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def _get_random_headers(self) -> Dict:
        """Generate random headers to avoid bot detection"""
        return {
            **self.headers,
            'User-Agent': self.user_agent.random,
            'Referer': f'{self.base_url}/'
        }

    def _get_property_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML with retries"""
        for _ in range(3):  # Retry 3 times
            try:
                response = self.session.get(
                    url,
                    headers=self._get_random_headers(),
                    timeout=10
                )
                response.raise_for_status()
                
                # Check if blocked
                if "captcha" in response.text.lower():
                    raise ValueError("CAPTCHA encountered")
                    
                return BeautifulSoup(response.text, 'html.parser')
                
            except Exception as e:
                print(f"Retrying... Error: {e}")
                time.sleep(random.uniform(2, 5))
        return None

    def scrape_property(self, zillow_url: str) -> Optional[Dict]:
        """Extract property data from Zillow URL"""
        soup = self._get_property_soup(zillow_url)
        if not soup:
            return None

        try:
            # Extract from JSON-LD (most reliable)
            script = soup.find('script', type='application/ld+json')
            if script:
                data = json.loads(script.string)
                return {
                    'address': data.get('address', {}).get('streetAddress'),
                    'price': data.get('offers', {}).get('price'),
                    'bedrooms': data.get('numberOfBedrooms'),
                    'bathrooms': data.get('numberOfBathrooms'),
                    'sqft': data.get('floorSize', {}).get('value'),
                    'lot_size': data.get('lotSize', {}).get('value'),
                    'year_built': data.get('yearBuilt'),
                    'zestimate': soup.find('span', {'data-testid': 'zestimate'}).text.strip() if soup.find('span', {'data-testid': 'zestimate'}) else None
                }

            # Fallback to HTML scraping
            return {
                'address': soup.find('h1', {'data-testid': 'address'}).text.strip(),
                'price': soup.find('span', {'data-testid': 'price'}).text.strip().replace('$', '').replace(',', ''),
                'bedrooms': soup.find('span', {'data-testid': 'bedrooms'}).text.strip().split()[0],
                'bathrooms': soup.find('span', {'data-testid': 'bathrooms'}).text.strip().split()[0],
                'sqft': soup.find('span', {'data-testid': 'floor-space'}).text.strip().replace(',', ''),
                'lot_size': soup.find('span', text='Lot Size').find_next_sibling('span').text if soup.find('span', text='Lot Size') else None,
                'year_built': soup.find('span', text='Year Built').find_next_sibling('span').text if soup.find('span', text='Year Built') else None
            }
        except Exception as e:
            print(f"Scraping failed: {e}")
            return None

if __name__ == "__main__":
    scraper = ZillowScraper()
    
    # Example Zillow property URL
    test_url = "https://www.zillow.com/homedetails/123-Main-St-Anytown-CA-12345/12345678_zpid/"
    
    property_data = scraper.scrape_property(test_url)
    print(json.dumps(property_data, indent=2))