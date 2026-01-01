"""
Scraper usando APIs públicas dos sites
Mais confiável e rápido que scraping HTML
"""
from typing import List, Dict
import requests
import time
import random
import re
import json


class ScraperAPIs:
    """Scraper que usa APIs internas públicas dos sites"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.mercadolivre.com.br',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
        })

    def _clean_price(self, price_str: str) -> float:
        """Limpa string de preço"""
        try:
            if isinstance(price_str, (int, float)):
                return float(price_str)
            price_str = re.sub(r'[^\d,.]', '', str(price_str))
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '')
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0

    def buscar_mercadolivre_api(self, termo: str) -> List[Dict]:
        """Busca no Mercado Livre via API oficial"""
        produtos = []

        try:
            # API pública do Mercado Livre
            url = "https://api.mercadolibre.com/sites/MLB/search"

            params = {
                'q': termo,
                'limit': 20,
                'offset': 0
            }

            print(f"   🔍 Mercado Livre API: {termo}")

            time.sleep(random.uniform(0.5, 1.5))

            response = self.session.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                items = data.get('results', [])

                for item in items[:15]:
                    try:
                        nome = item.get('title', '')
                        preco = item.get('price', 0)

                        if not nome or preco == 0:
                            continue

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': float(preco),
                            'preco_original': item.get('original_price'),
                            'em_promocao': item.get('original_price') is not None,
                            'url': item.get('permalink', ''),
                            'supermercado': 'Mercado Livre',
                            'disponivel': item.get('available_quantity', 0) > 0,
                            'imagem': item.get('thumbnail', '')
                        })

                    except Exception as e:
                        continue

                print(f"   ✅ Mercado Livre API: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Mercado Livre API: {e}")

        return produtos

    def buscar_americanas_api(self, termo: str) -> List[Dict]:
        """Busca nas Americanas via API"""
        produtos = []

        try:
            # API de busca das Americanas
            url = "https://mystique-v2-americanas.b2w.io/search"

            params = {
                'query': termo,
                'page': 1,
                'rows': 15,
                'source': 'omega'
            }

            headers = {
                **self.session.headers,
                'referer': 'https://www.americanas.com.br/',
                'origin': 'https://www.americanas.com.br'
            }

            print(f"   🔍 Americanas API: {termo}")

            time.sleep(random.uniform(0.5, 1.5))

            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                items = data.get('products', [])

                for item in items[:15]:
                    try:
                        nome = item.get('name', '')
                        preco_info = item.get('offers', {}).get('price', 0)
                        preco = self._clean_price(preco_info)

                        if not nome or preco == 0:
                            continue

                        produtos.append({
                            'nome': nome,
                            'marca': item.get('brand', {}).get('name'),
                            'preco': preco,
                            'em_promocao': item.get('offers', {}).get('onSale', False),
                            'url': f"https://www.americanas.com.br/produto/{item.get('id', '')}",
                            'supermercado': 'Americanas',
                            'disponivel': True
                        })

                    except Exception as e:
                        continue

                print(f"   ✅ Americanas API: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Americanas API: {e}")

        return produtos

    def buscar_shopee_api(self, termo: str) -> List[Dict]:
        """Busca na Shopee via API"""
        produtos = []

        try:
            url = "https://shopee.com.br/api/v4/search/search_items"

            params = {
                'by': 'relevancy',
                'keyword': termo,
                'limit': 15,
                'newest': 0,
                'order': 'desc',
                'page_type': 'search',
                'scenario': 'PAGE_GLOBAL_SEARCH',
                'version': 2
            }

            headers = {
                **self.session.headers,
                'referer': 'https://shopee.com.br/',
                'origin': 'https://shopee.com.br',
                'x-requested-with': 'XMLHttpRequest'
            }

            print(f"   🔍 Shopee API: {termo}")

            time.sleep(random.uniform(0.5, 1.5))

            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                items = data.get('items', [])

                for item_wrapper in items[:15]:
                    try:
                        item = item_wrapper.get('item_basic', {})

                        nome = item.get('name', '')
                        preco_centavos = item.get('price', 0)
                        preco = preco_centavos / 100000  # Shopee usa preço em centavos * 1000

                        if not nome or preco == 0:
                            continue

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': item.get('raw_discount', 0) > 0,
                            'url': f"https://shopee.com.br/product/{item.get('shopid', '')}/{item.get('itemid', '')}",
                            'supermercado': 'Shopee',
                            'disponivel': item.get('stock', 0) > 0
                        })

                    except Exception as e:
                        continue

                print(f"   ✅ Shopee API: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Shopee API: {e}")

        return produtos

    def buscar_todos(self, termo: str, max_por_fonte: int = 15) -> List[Dict]:
        """Busca em todas as APIs"""
        print(f"\n{'='*60}")
        print(f"🚀 API SCRAPER: '{termo}'")
        print(f"{'='*60}")

        todos_produtos = []

        # Buscar em paralelo seria melhor, mas por enquanto sequencial
        fontes = [
            ('Mercado Livre', self.buscar_mercadolivre_api),
            ('Americanas', self.buscar_americanas_api),
            ('Shopee', self.buscar_shopee_api),
        ]

        for nome_fonte, metodo_busca in fontes:
            try:
                produtos = metodo_busca(termo)
                todos_produtos.extend(produtos[:max_por_fonte])

                # Delay entre fontes
                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"   ❌ Erro em {nome_fonte}: {e}")

        # Remover duplicatas
        produtos_unicos = {}
        for p in todos_produtos:
            key = f"{p['nome'][:40].lower()}_{p['supermercado']}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        resultado = list(produtos_unicos.values())

        print(f"\n{'='*60}")
        print(f"✅ TOTAL: {len(resultado)} produtos via APIs")
        print(f"{'='*60}\n")

        return resultado


# Instância global
scraper_apis = ScraperAPIs()
