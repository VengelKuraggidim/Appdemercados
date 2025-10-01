from .base import BaseScraper
from typing import List, Dict
from urllib.parse import quote


class MercadoLivreScraper(BaseScraper):
    """Scraper for Mercado Livre marketplace"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.mercadolivre.com.br"

    def get_supermercado_name(self) -> str:
        return "mercado_livre"

    def search(self, termo: str) -> List[Dict]:
        """Search for products on Mercado Livre"""
        termo_encoded = quote(termo)
        # Add category filter for grocery items
        search_url = f"{self.base_url}/jm/search?as_word={termo_encoded}"

        soup = self._get_page(search_url)
        if not soup:
            return []

        produtos = []

        # Mercado Livre uses ol > li structure for search results
        product_items = soup.find_all('li', class_=lambda x: x and 'ui-search-layout__item' in str(x)) or \
                       soup.find_all('div', class_=lambda x: x and 'ui-search-result' in str(x))

        for item in product_items[:20]:
            try:
                # Extract product name
                nome_elem = item.find('h2', class_=lambda x: x and 'ui-search-item__title' in str(x)) or \
                           item.find('a', class_=lambda x: x and 'ui-search-link' in str(x))
                if not nome_elem:
                    continue
                nome = nome_elem.text.strip()

                # Extract price
                preco_elem = item.find('span', class_=lambda x: x and 'andes-money-amount__fraction' in str(x)) or \
                            item.find('span', class_=lambda x: x and 'price-tag-fraction' in str(x))
                if not preco_elem:
                    continue

                preco_text = preco_elem.text.strip()
                preco = self._clean_price(preco_text)
                if not preco:
                    continue

                # Extract URL
                link_elem = item.find('a', href=True)
                url = link_elem['href'] if link_elem else ""

                # Check if it's on sale (free shipping can indicate better deals)
                em_promocao = bool(item.find(string=lambda x: x and 'frete grátis' in str(x).lower()))

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
                print(f"Error parsing Mercado Livre product: {e}")
                continue

        return produtos
