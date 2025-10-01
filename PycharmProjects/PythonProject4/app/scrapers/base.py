from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import random


class BaseScraper(ABC):
    """Base class for all supermarket scrapers"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    @abstractmethod
    def search(self, termo: str) -> List[Dict]:
        """Search for products by term"""
        pass

    @abstractmethod
    def get_supermercado_name(self) -> str:
        """Return the supermarket name"""
        pass

    def _get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Get page content with retries"""
        for attempt in range(retries):
            try:
                time.sleep(random.uniform(1, 3))  # Random delay to avoid blocking
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            except Exception as e:
                if attempt == retries - 1:
                    print(f"Error fetching {url}: {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def _clean_price(self, price_str: str) -> Optional[float]:
        """Clean and convert price string to float"""
        try:
            # Remove R$, spaces, and convert comma to dot
            price_str = price_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(price_str)
        except:
            return None
