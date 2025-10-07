from .base import BaseScraper
from typing import List, Dict
from urllib.parse import quote
import re


class GoogleShoppingScraper(BaseScraper):
    """Scraper for Google Shopping results"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.google.com"
        # Update headers for Google
        self.headers.update({
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Referer': 'https://www.google.com/',
        })

    def get_supermercado_name(self) -> str:
        return "google_shopping"

    def search(self, termo: str) -> List[Dict]:
        """Search for products on Google Shopping"""
        termo_encoded = quote(termo)
        # Use Google Shopping search
        search_url = f"{self.base_url}/search?q={termo_encoded}+preço+supermercado&tbm=shop"

        print(f"🔍 Buscando no Google Shopping: {termo}")
        soup = self._get_page(search_url)
        if not soup:
            # Try regular Google search with shopping intent
            search_url = f"{self.base_url}/search?q={termo_encoded}+preço+comprar"
            soup = self._get_page(search_url)
            if not soup:
                return []

        produtos = []

        # Try Google Shopping cards
        shopping_cards = soup.find_all('div', class_=lambda x: x and ('sh-dgr__content' in str(x) or 'shopping' in str(x).lower()))

        # Also try regular search results with price
        if not shopping_cards:
            shopping_cards = soup.find_all('div', class_='g') + \
                           soup.find_all('div', {'data-hveid': True})

        print(f"   Encontrados {len(shopping_cards)} cards para analisar")

        for card in shopping_cards[:30]:
            try:
                # Extract product name
                nome_elem = card.find(['h3', 'h4']) or \
                           card.find(class_=lambda x: x and 'title' in str(x).lower())

                if not nome_elem:
                    continue

                nome = nome_elem.text.strip()

                # Skip if doesn't look like a product
                if len(nome) < 5 or 'Google' in nome:
                    continue

                # Extract price - look for R$ pattern
                price_patterns = [
                    r'R\$\s*(\d+[.,]\d{2})',
                    r'(\d+[.,]\d{2})\s*reais?',
                    r'por\s+R?\$?\s*(\d+[.,]\d{2})',
                ]

                preco = None
                preco_text = card.get_text()

                for pattern in price_patterns:
                    match = re.search(pattern, preco_text, re.IGNORECASE)
                    if match:
                        preco_str = match.group(1) if match.group(1) else match.group(0)
                        preco = self._clean_price(preco_str)
                        if preco:
                            break

                if not preco or preco <= 0 or preco > 100000:
                    continue

                # Extract URL
                link_elem = card.find('a', href=True)
                url = link_elem['href'] if link_elem else ""
                if url.startswith('/url?q='):
                    # Extract actual URL from Google redirect
                    url = url.split('/url?q=')[1].split('&')[0]
                elif url.startswith('/'):
                    url = self.base_url + url

                # Try to identify the store/supermarket from the URL or text
                supermercado = self._identificar_supermercado(url, card.get_text())

                # Check if it's on sale
                em_promocao = bool(re.search(r'(promoção|oferta|desconto|%\s*off)', preco_text, re.IGNORECASE))

                # Extract brand if possible
                marca = None
                marca_patterns = [
                    r'Marca:\s*([A-Za-zÀ-ú\s]+)',
                    r'marca\s+([A-Za-zÀ-ú]+)',
                ]
                for pattern in marca_patterns:
                    match = re.search(pattern, preco_text, re.IGNORECASE)
                    if match:
                        marca = match.group(1).strip()
                        break

                produtos.append({
                    'nome': nome,
                    'marca': marca,
                    'preco': preco,
                    'em_promocao': em_promocao,
                    'url': url,
                    'supermercado': supermercado,
                    'disponivel': True
                })

                print(f"   ✓ {nome[:40]}... - R$ {preco:.2f} ({supermercado})")

            except Exception as e:
                print(f"   ✗ Erro ao processar card: {e}")
                continue

        print(f"   Total extraído: {len(produtos)} produtos")
        return produtos

    def _identificar_supermercado(self, url: str, texto: str) -> str:
        """Identify the supermarket from URL or text"""
        url_lower = url.lower()
        texto_lower = texto.lower()

        # Map of keywords to supermarket names
        mercados = {
            'carrefour': 'carrefour',
            'paodeacucar': 'pao_acucar',
            'pão de açúcar': 'pao_acucar',
            'extra': 'extra',
            'mercadolivre': 'mercado_livre',
            'mercado livre': 'mercado_livre',
            'atacadao': 'atacadao',
            'atacadão': 'atacadao',
            'walmart': 'walmart',
            'prezunic': 'prezunic',
            'assai': 'assai',
            'assaí': 'assai',
            'makro': 'makro',
            'sam': 'sams_club',
            'tenda': 'tenda',
            'big': 'big',
            'bompreco': 'bompreco',
            'bom preço': 'bompreco',
            'supermercado': 'supermercado',
            'magazine': 'magazine_luiza',
            'americanas': 'americanas',
            'submarino': 'submarino',
            'casas bahia': 'casas_bahia',
        }

        # Check URL first (more reliable)
        for keyword, name in mercados.items():
            if keyword.replace(' ', '') in url_lower.replace('-', '').replace('_', ''):
                return name

        # Check text
        for keyword, name in mercados.items():
            if keyword in texto_lower:
                return name

        return 'online'  # Generic online store
