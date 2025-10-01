from .base import BaseScraper
from typing import List, Dict
from urllib.parse import quote


class ExtraScraper(BaseScraper):
    """Scraper for Extra supermarket"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.extra.com.br"

    def get_supermercado_name(self) -> str:
        return "extra"

    def search(self, termo: str) -> List[Dict]:
        """Search for products on Extra"""
        termo_encoded = quote(termo)
        search_url = f"{self.base_url}/busca/?q={termo_encoded}"

        soup = self._get_page(search_url)
        if not soup:
            return []

        produtos = []

        # Extra product cards
        product_cards = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower()) or \
                       soup.find_all('li', class_=lambda x: x and 'item' in str(x).lower())

        for card in product_cards[:20]:
            try:
                # Extract product name
                nome_elem = card.find(['h2', 'h3', 'h4', 'span'], class_=lambda x: x and 'name' in str(x).lower()) or \
                           card.find('a', class_=lambda x: x and 'title' in str(x).lower())
                if not nome_elem:
                    continue
                nome = nome_elem.text.strip() if hasattr(nome_elem, 'text') else nome_elem.get('title', '').strip()

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
                em_promocao = bool(card.find(class_=lambda x: x and ('discount' in str(x).lower() or 'sale' in str(x).lower())))

                produtos.append({
                    'nome': nome,
                    'marca': None,
                    'preco': preco,
                    'em_promocao': em_promocao,
                    'url': url,
                    'supermercado': self.get_supermercado_name(),
                    'disponivel': True
                })

            except Exception as e:
                print(f"Error parsing Extra product: {e}")
                continue

        return produtos
