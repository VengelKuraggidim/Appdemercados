from .base import BaseScraper
from typing import List, Dict
from urllib.parse import quote


class CarrefourScraper(BaseScraper):
    """Scraper for Carrefour supermarket"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.carrefour.com.br"

    def get_supermercado_name(self) -> str:
        return "carrefour"

    def search(self, termo: str) -> List[Dict]:
        """Search for products on Carrefour"""
        termo_encoded = quote(termo)
        search_url = f"{self.base_url}/s?q={termo_encoded}"

        soup = self._get_page(search_url)
        if not soup:
            return []

        produtos = []

        # Carrefour uses specific CSS classes for product cards
        product_cards = soup.find_all('div', {'data-testid': 'product-card'}) or \
                       soup.find_all('article', class_=lambda x: x and 'product' in x.lower())

        for card in product_cards[:20]:  # Limit to 20 products
            try:
                # Extract product name
                nome_elem = card.find('h2') or card.find('h3') or card.find(class_=lambda x: x and 'title' in str(x).lower())
                if not nome_elem:
                    continue
                nome = nome_elem.text.strip()

                # Extract price
                preco_elem = card.find(class_=lambda x: x and 'price' in str(x).lower())
                if not preco_elem:
                    continue

                preco_text = preco_elem.text.strip()
                preco = self._clean_price(preco_text)
                if not preco:
                    continue

                # Extract URL
                link_elem = card.find('a', href=True)
                url = link_elem['href'] if link_elem else ""
                if url and not url.startswith('http'):
                    url = self.base_url + url

                # Check if it's on sale
                em_promocao = bool(card.find(class_=lambda x: x and ('promo' in str(x).lower() or 'sale' in str(x).lower())))

                # Extract brand
                marca_elem = card.find(class_=lambda x: x and 'brand' in str(x).lower())
                marca = marca_elem.text.strip() if marca_elem else None

                produtos.append({
                    'nome': nome,
                    'marca': marca,
                    'preco': preco,
                    'em_promocao': em_promocao,
                    'url': url,
                    'supermercado': self.get_supermercado_name(),
                    'disponivel': True
                })

            except Exception as e:
                print(f"Error parsing Carrefour product: {e}")
                continue

        return produtos
