from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .carrefour import CarrefourScraper
from .pao_acucar import PaoAcucarScraper
from .extra import ExtraScraper
from .mercado_livre import MercadoLivreScraper
from .google_shopping import GoogleShoppingScraper
from .atacadao import AtacadaoScraper
from .assai import AssaiScraper
from .dia import DiaScraper


class ScraperManager:
    """Manages all scrapers and coordinates searches"""

    def __init__(self, usar_google: bool = True):
        if usar_google:
            # Use Google Shopping as primary source
            self.scrapers = {
                'google_shopping': GoogleShoppingScraper(),
            }
        else:
            # Use direct scrapers (may be blocked)
            self.scrapers = {
                'carrefour': CarrefourScraper(),
                'pao_acucar': PaoAcucarScraper(),
                'extra': ExtraScraper(),
                """'mercado_livre': MercadoLivreScraper(),
                'atacadao': AtacadaoScraper(),
                'assai': AssaiScraper(),
                'dia': DiaScraper(),
            }"""

    def search_all(self, termo: str, supermercados: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for products in all or specified supermarkets
        Uses parallel execution for faster results
        """
        if supermercados:
            active_scrapers = {k: v for k, v in self.scrapers.items() if k in supermercados}
        else:
            active_scrapers = self.scrapers

        all_produtos = []

        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=len(active_scrapers)) as executor:
            future_to_scraper = {
                executor.submit(scraper.search, termo): name
                for name, scraper in active_scrapers.items()
            }

            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    produtos = future.result(timeout=30)
                    all_produtos.extend(produtos)
                    print(f"✓ {scraper_name}: {len(produtos)} produtos encontrados")
                except Exception as e:
                    print(f"✗ {scraper_name}: Erro ao buscar - {e}")

        return all_produtos

    def search_single(self, termo: str, supermercado: str) -> List[Dict]:
        """Search in a single supermarket"""
        if supermercado not in self.scrapers:
            raise ValueError(f"Supermercado '{supermercado}' não suportado")

        scraper = self.scrapers[supermercado]
        return scraper.search(termo)

    def get_available_supermarkets(self) -> List[str]:
        """Get list of available supermarkets"""
        return list(self.scrapers.keys())
