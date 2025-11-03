import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple

logger = logging.getLogger(__name__)

class ProxyManager:
    def __init__(self):
        self.cache_file = '/tmp/proxy_cache.json'
        self.proxies: List[Dict] = []
        self.current_index = 0
        self.last_fetch_time = None
        self.fetch_interval = 3600
        self.lock = threading.Lock()
        self.enabled = os.environ.get('ENABLE_PROXY_ROTATION', 'false').lower() == 'true'
        self.test_timeout = int(os.environ.get('PROXY_TEST_TIMEOUT', '5'))
        self.max_proxies = int(os.environ.get('MAX_PROXY_CACHE', '20'))
        
        if self.enabled:
            logger.info("Proxy rotation enabled")
            self._load_cache()
        else:
            logger.info("Proxy rotation disabled (set ENABLE_PROXY_ROTATION=true to enable)")
    
    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.proxies = data.get('proxies', [])
                    last_fetch = data.get('last_fetch_time')
                    if last_fetch:
                        self.last_fetch_time = datetime.fromisoformat(last_fetch)
                    logger.info(f"Loaded {len(self.proxies)} cached proxies")
        except Exception as e:
            logger.warning(f"Could not load proxy cache: {e}")
            self.proxies = []
    
    def _save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'proxies': self.proxies,
                    'last_fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None
                }, f)
        except Exception as e:
            logger.warning(f"Could not save proxy cache: {e}")
    
    def _fetch_free_proxies(self) -> List[Dict]:
        proxies = []
        
        apis = [
            {
                'name': 'ProxyScrape',
                'url': 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'parser': self._parse_proxyscrape
            },
            {
                'name': 'GeoNode',
                'url': 'https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps',
                'parser': self._parse_geonode
            }
        ]
        
        for api in apis:
            try:
                logger.info(f"Fetching proxies from {api['name']}...")
                import requests
                response = requests.get(api['url'], timeout=10)
                if response.status_code == 200:
                    new_proxies = api['parser'](response)
                    proxies.extend(new_proxies)
                    logger.info(f"Fetched {len(new_proxies)} proxies from {api['name']}")
            except Exception as e:
                logger.warning(f"Failed to fetch from {api['name']}: {e}")
                continue
        
        return proxies
    
    def _parse_proxyscrape(self, response) -> List[Dict]:
        proxies = []
        try:
            lines = response.text.strip().split('\n')
            for line in lines[:50]:
                line = line.strip()
                if line and ':' in line:
                    proxies.append({
                        'url': f'http://{line}',
                        'tested': False,
                        'success_count': 0,
                        'fail_count': 0
                    })
        except Exception as e:
            logger.warning(f"ProxyScrape parsing error: {e}")
        return proxies
    
    def _parse_geonode(self, response) -> List[Dict]:
        proxies = []
        try:
            data = response.json()
            for item in data.get('data', [])[:50]:
                ip = item.get('ip')
                port = item.get('port')
                protocols = item.get('protocols', [])
                
                if ip and port and protocols:
                    protocol = 'https' if 'https' in protocols else 'http'
                    proxies.append({
                        'url': f'{protocol}://{ip}:{port}',
                        'tested': False,
                        'success_count': 0,
                        'fail_count': 0
                    })
        except Exception as e:
            logger.warning(f"GeoNode parsing error: {e}")
        return proxies
    
    def _test_proxy(self, proxy_url: str) -> bool:
        try:
            import requests
            test_url = 'https://www.google.com'
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            response = requests.get(test_url, proxies=proxies, timeout=self.test_timeout)
            return response.status_code == 200
        except:
            return False
    
    def _refresh_proxies(self):
        with self.lock:
            now = datetime.now()
            
            if self.last_fetch_time:
                time_since_fetch = (now - self.last_fetch_time).total_seconds()
                if time_since_fetch < self.fetch_interval and len(self.proxies) > 0:
                    logger.debug(f"Using cached proxies ({int(time_since_fetch)}s since last fetch)")
                    return
            
            logger.info("Refreshing proxy list...")
            new_proxies = self._fetch_free_proxies()
            
            if new_proxies:
                logger.info(f"Testing {len(new_proxies)} proxies (timeout: {self.test_timeout}s)...")
                tested_proxies = []
                
                for i, proxy in enumerate(new_proxies[:30]):
                    if self._test_proxy(proxy['url']):
                        proxy['tested'] = True
                        proxy['success_count'] = 1
                        tested_proxies.append(proxy)
                        logger.info(f"✓ Working proxy found: {proxy['url']}")
                        
                        if len(tested_proxies) >= self.max_proxies:
                            break
                    
                    if i > 0 and i % 10 == 0:
                        logger.info(f"Tested {i}/{len(new_proxies[:30])} proxies, found {len(tested_proxies)} working")
                
                if tested_proxies:
                    self.proxies = tested_proxies
                    self.current_index = 0
                    self.last_fetch_time = now
                    self._save_cache()
                    logger.info(f"✓ Proxy refresh complete: {len(self.proxies)} working proxies available")
                else:
                    logger.warning("No working proxies found during refresh")
            else:
                logger.warning("Failed to fetch any proxies from APIs")
    
    def get_proxy(self) -> Optional[str]:
        if not self.enabled:
            return None
        
        if not self.proxies or (self.last_fetch_time and 
            (datetime.now() - self.last_fetch_time).total_seconds() > self.fetch_interval):
            self._refresh_proxies()
        
        if not self.proxies:
            logger.warning("No proxies available")
            return None
        
        with self.lock:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            logger.info(f"Using proxy {self.current_index}/{len(self.proxies)}: {proxy['url']}")
            return proxy['url']
    
    def mark_proxy_success(self, proxy_url: str):
        if not self.enabled or not proxy_url:
            return
        
        with self.lock:
            for proxy in self.proxies:
                if proxy['url'] == proxy_url:
                    proxy['success_count'] = proxy.get('success_count', 0) + 1
                    proxy['fail_count'] = max(0, proxy.get('fail_count', 0) - 1)
                    break
            self._save_cache()
    
    def mark_proxy_failed(self, proxy_url: str):
        if not self.enabled or not proxy_url:
            return
        
        with self.lock:
            for i, proxy in enumerate(self.proxies):
                if proxy['url'] == proxy_url:
                    proxy['fail_count'] = proxy.get('fail_count', 0) + 1
                    
                    if proxy['fail_count'] >= 3:
                        logger.warning(f"Removing failed proxy: {proxy_url}")
                        self.proxies.pop(i)
                        if self.current_index >= len(self.proxies):
                            self.current_index = 0
                    break
            self._save_cache()
    
    def get_next_proxy_with_fallback(self) -> Tuple[Optional[str], bool]:
        proxy = self.get_proxy()
        if proxy:
            return proxy, True
        return None, False
    
    def get_stats(self) -> Dict:
        with self.lock:
            return {
                'enabled': self.enabled,
                'total_proxies': len(self.proxies),
                'current_index': self.current_index,
                'last_fetch': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
                'cache_age_seconds': int((datetime.now() - self.last_fetch_time).total_seconds()) if self.last_fetch_time else None
            }

proxy_manager = ProxyManager()
