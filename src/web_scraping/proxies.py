import requests
import random
import time
from src.config import PROXY_SETTINGS
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

class FreeProxyManager:
    """
    A class to manage free proxies for web scraping with automatic:
    - Proxy fetching from multiple free sources
    - Proxy validation
    - Proxy rotation
    - Automatic retries
    """
    
    def __init__(self, max_proxies: int = 20, verify_ssl: bool = False):
        self.proxy_sources = [
            self._get_geonode_proxies,
            self._get_proxyscrape_proxies,
            self._get_freeproxy_proxies
        ]
        self.working_proxies = []
        self.max_proxies = max_proxies
        self.verify_ssl = verify_ssl
        self.last_refresh = 0
        self.refresh_interval = 3600  # 1 hour
        
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a random working proxy"""
        if not self.working_proxies or time.time() - self.last_refresh > self.refresh_interval:
            self.refresh_proxies()
            
        if not self.working_proxies:
            return None
            
        return random.choice(self.working_proxies)
    
    def refresh_proxies(self) -> None:
        """Refresh the list of working proxies"""
        print("Refreshing proxy list...")
        raw_proxies = set()
        
        # Fetch proxies from all sources in parallel
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda f: f(), self.proxy_sources)
            for proxy_list in results:
                raw_proxies.update(proxy_list)
        
        # Test proxies in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            test_results = executor.map(self._test_proxy, raw_proxies)
            
        self.working_proxies = [
            {"http": proxy, "https": proxy} 
            for proxy, is_working in zip(raw_proxies, test_results) 
            if is_working
        ][:self.max_proxies]
        
        self.last_refresh = time.time()
        print(f"Found {len(self.working_proxies)} working proxies")
    
    def _test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        try:
            response = requests.get(
                "http://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=5,
                verify=self.verify_ssl
            )
            return response.status_code == 200
        except:
            return False
    
    # Proxy Source Providers
    def _get_geonode_proxies(self) -> List[str]:
        """Fetch proxies from Geonode API"""
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url, timeout=10)
            return [
                f"http://{p['ip']}:{p['port']}"
                for p in response.json().get('data', [])
                if p.get('protocols', ['http']) and 'http' in p['protocols']
            ]
        except:
            return []
    
    def _get_proxyscrape_proxies(self) -> List[str]:
        """Fetch proxies from ProxyScrape"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all"
            response = requests.get(url, timeout=10)
            return [
                f"http://{line.strip()}"
                for line in response.text.split('\n')
                if line.strip()
            ]
        except:
            return []
    
    def _get_freeproxy_proxies(self) -> List[str]:
        """Fetch proxies from FreeProxyList"""
        try:
            url = "https://free-proxy-list.net/"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            proxies = []
            
            for row in soup.select('table#proxylisttable tbody tr'):
                cols = row.find_all('td')
                if cols[6].text == 'yes':  # HTTPS support
                    proxy = f"http://{cols[0].text}:{cols[1].text}"
                    proxies.append(proxy)
            return proxies
        except:
            return []

# Singleton instance for easy access
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.last_refresh = 0
        
    def get_proxy(self):
        if not PROXY_SETTINGS['enabled']:
            return None
            
        if (time.time() - self.last_refresh > PROXY_SETTINGS['refresh_interval'] 
            or not self.proxies):
            self.refresh_proxies()
            
        return random.choice(self.proxies) if self.proxies else None
    
proxy_manager = FreeProxyManager()

def get_proxy() -> Optional[Dict[str, str]]:
    """Public interface to get a random working proxy"""
    return proxy_manager.get_proxy()

def refresh_proxies() -> None:
    """Public interface to refresh proxies"""
    proxy_manager.refresh_proxies()