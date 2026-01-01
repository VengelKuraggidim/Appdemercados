"""
Scraper para Atacadao (atacadao.com.br)
"""
from typing import List, Dict
from urllib.parse import quote
from .base import BaseScraper


class AtacadaoScraper(BaseScraper):
    """Scraper para o Atacadao"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.atacadao.com.br"

    def get_supermercado_name(self) -> str:
        return "atacadao"

    def search(self, termo: str) -> List[Dict]:
        """Busca produtos no Atacadao"""
        termo_encoded = quote(termo)
        search_url = f"{self.base_url}/busca?q={termo_encoded}"

        soup = self._get_page(search_url)
        if not soup:
            return []

        produtos = []

        # Tenta diferentes seletores para produtos
        product_selectors = [
            'div[data-testid="product-card"]',
            'div.product-card',
            'article.product',
            'div.vtex-search-result-3-x-galleryItem',
            'div[class*="product"]'
        ]

        product_cards = []
        for selector in product_selectors:
            product_cards = soup.select(selector)
            if product_cards:
                break

        for card in product_cards[:20]:
            try:
                # Nome do produto
                nome_elem = card.find(['h2', 'h3', 'h4']) or card.select_one('[class*="name"], [class*="title"]')
                if not nome_elem:
                    continue
                nome = nome_elem.get_text(strip=True)
                if len(nome) < 3:
                    continue

                # Preco
                preco_elem = card.select_one('[class*="price"], [class*="preco"], .price')
                if not preco_elem:
                    continue
                preco = self._clean_price(preco_elem.get_text())
                if not preco:
                    continue

                # URL do produto
                link = card.find('a', href=True)
                url = ""
                if link:
                    url = link['href']
                    if url and not url.startswith('http'):
                        url = self.base_url + url

                # Marca (opcional)
                marca_elem = card.select_one('[class*="brand"], [class*="marca"]')
                marca = marca_elem.get_text(strip=True) if marca_elem else None

                # Promocao
                em_promocao = bool(card.select_one('[class*="promo"], [class*="oferta"], [class*="desconto"]'))

                produtos.append({
                    'nome': nome,
                    'marca': marca,
                    'preco': preco,
                    'url': url,
                    'supermercado': self.get_supermercado_name(),
                    'disponivel': True,
                    'em_promocao': em_promocao
                })

            except Exception as e:
                continue

        return produtos
