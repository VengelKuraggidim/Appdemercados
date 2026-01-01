from .base import BaseScraper
from typing import List, Dict
from urllib.parse import quote


class PaoAcucarScraper(BaseScraper):
    """Scraper for Pão de Açúcar supermarket"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.paodeacucar.com"

    def get_supermercado_name(self) -> str:
        return "pao_acucar"

    def search(self, termo: str) -> List[Dict]:
        """Search for products on Pão de Açúcar"""
        termo_encoded = quote(termo)
        search_url = f"{self.base_url}/busca?q={termo_encoded}"

        soup = self._get_page(search_url)
        if not soup:
            return []

        produtos = []

        # Pão de Açúcar product structure
        product_cards = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower()) or \
                       soup.find_all('article') or \
                       soup.find_all('li', class_=lambda x: x and 'item' in str(x).lower())

        for card in product_cards[:20]:
            try:
                # Extract product name
                nome_elem = card.find(['h2', 'h3', 'h4']) or \
                           card.find(class_=lambda x: x and ('name' in str(x).lower() or 'title' in str(x).lower()))
                if not nome_elem:
                    continue
                nome = nome_elem.text.strip()

                # Extract price
                preco_elem = card.find(class_=lambda x: x and 'price' in str(x).lower()) or \
                            card.find('span', string=lambda x: x and 'R$' in str(x))
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
                em_promocao = bool(card.find(string=lambda x: x and ('oferta' in str(x).lower() or 'promoção' in str(x).lower())))

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
                print(f"Error parsing Pão de Açúcar product: {e}")
                continue

        return produtos
