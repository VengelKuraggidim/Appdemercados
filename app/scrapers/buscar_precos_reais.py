"""
Busca precos REAIS de produtos na internet
Faz scraping de multiplas fontes para encontrar precos reais
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus, urlencode


class BuscadorPrecosReais:
    """
    Busca precos reais de produtos na internet
    Usa multiplas fontes: Mercado Livre, Amazon, Americanas, Shopee, etc.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
        }
        # Cache simples para evitar buscas repetidas
        self._cache = {}
        self._cache_timeout = 300  # 5 minutos

    def _fazer_request(self, url: str, timeout: int = 15, extra_headers: dict = None) -> requests.Response:
        """Faz request HTTP de forma thread-safe"""
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        return requests.get(url, headers=headers, timeout=timeout)

    def buscar(self, termo: str, limite: int = 20) -> List[Dict]:
        """
        Busca precos reais para um produto
        Usa threading para buscar em paralelo de multiplas fontes
        """
        print(f"\n{'='*60}")
        print(f"[BUSCA REAL] BUSCANDO PRECOS: '{termo}'")
        print(f"{'='*60}")

        resultados = []

        # Lista de fontes para buscar em paralelo
        fontes = [
            ('Mercado Livre', self._buscar_mercadolivre),
            ('Amazon Brasil', self._buscar_amazon),
            ('Americanas', self._buscar_americanas),
            ('Magazine Luiza', self._buscar_magalu),
            ('Casas Bahia', self._buscar_casasbahia),
            ('Carrefour', self._buscar_carrefour),
            ('Extra', self._buscar_extra),
            ('Shopee', self._buscar_shopee),
            ('DuckDuckGo', self._buscar_duckduckgo),
            ('Google Shopping', self._buscar_google_shopping),
        ]

        # Buscar em paralelo para maior velocidade
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for nome_fonte, funcao in fontes:
                future = executor.submit(self._buscar_seguro, nome_fonte, funcao, termo)
                futures[future] = nome_fonte

            for future in as_completed(futures, timeout=30):
                nome_fonte = futures[future]
                try:
                    produtos = future.result()
                    if produtos:
                        print(f"   [OK] {nome_fonte}: {len(produtos)} produtos")
                        resultados.extend(produtos)
                    else:
                        print(f"   [!] {nome_fonte}: Nenhum resultado")
                except Exception as e:
                    print(f"   [X] {nome_fonte}: Erro - {str(e)[:40]}")

        # Remover duplicatas e ordenar por preco
        resultados_unicos = self._remover_duplicatas(resultados)
        resultados_unicos.sort(key=lambda x: x.get('preco', float('inf')))

        print(f"\n   [TOTAL] {len(resultados_unicos)} produtos REAIS encontrados")
        print(f"{'='*60}\n")

        return resultados_unicos[:limite]

    def _buscar_seguro(self, nome: str, funcao, termo: str) -> List[Dict]:
        """Wrapper para capturar erros de cada fonte"""
        try:
            return funcao(termo)
        except Exception as e:
            print(f"      Erro {nome}: {e}")
            return []

    def _buscar_mercadolivre(self, termo: str) -> List[Dict]:
        """Busca no Mercado Livre - fonte principal"""
        produtos = []

        termo_formatado = termo.replace(' ', '-')
        url = f"https://lista.mercadolivre.com.br/{termo_formatado}"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Multiplos seletores para diferentes layouts do ML
            seletores = [
                '.ui-search-result__wrapper',
                '.ui-search-layout__item',
                '.andes-card',
                '[class*="ui-search-result"]'
            ]

            cards = []
            for seletor in seletores:
                cards = soup.select(seletor)
                if cards:
                    break

            for card in cards[:20]:
                try:
                    # Nome - seletores atualizados do ML
                    nome = None
                    for sel in ['.poly-component__title', 'h3.poly-component__title-wrapper', '.ui-search-item__title', 'h2 a', 'h3 a']:
                        elem = card.select_one(sel)
                        if elem:
                            nome = elem.get_text(strip=True)
                            if nome:
                                break

                    # Preco
                    preco = None
                    preco_elem = card.select_one('.andes-money-amount__fraction')
                    if preco_elem:
                        preco_texto = preco_elem.get_text(strip=True).replace('.', '').replace(',', '')
                        centavos_elem = card.select_one('.andes-money-amount__cents')
                        centavos = centavos_elem.get_text(strip=True) if centavos_elem else '00'
                        try:
                            preco = float(f"{preco_texto}.{centavos}")
                        except:
                            pass

                    # Link
                    link_elem = card.select_one('a[href*="mercadolivre"]') or card.select_one('a[href*="mercadolibre"]') or card.select_one('a')
                    link = link_elem.get('href', '') if link_elem else ''

                    if nome and preco and preco > 0:
                        produtos.append({
                            'nome': nome[:120],
                            'preco': preco,
                            'supermercado': 'Mercado Livre',
                            'url': link,
                            'fonte': 'mercadolivre',
                            'disponivel': True
                        })
                except:
                    continue

        except Exception as e:
            pass

        return produtos

    def _buscar_amazon(self, termo: str) -> List[Dict]:
        """Busca na Amazon Brasil"""
        produtos = []

        termo_formatado = quote_plus(termo)
        url = f"https://www.amazon.com.br/s?k={termo_formatado}"

        try:
            extra_headers = {'Accept': 'text/html,application/xhtml+xml'}
            response = self._fazer_request(url, extra_headers=extra_headers)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Cards de produtos Amazon
            cards = soup.select('[data-component-type="s-search-result"]')

            for card in cards[:15]:
                try:
                    # Nome
                    nome_elem = card.select_one('h2 span') or card.select_one('.a-text-normal')
                    nome = nome_elem.get_text(strip=True) if nome_elem else None

                    # Preco
                    preco = None
                    preco_inteiro = card.select_one('.a-price-whole')
                    preco_decimal = card.select_one('.a-price-fraction')

                    if preco_inteiro:
                        inteiro = preco_inteiro.get_text(strip=True).replace('.', '').replace(',', '')
                        decimal = preco_decimal.get_text(strip=True) if preco_decimal else '00'
                        try:
                            preco = float(f"{inteiro}.{decimal}")
                        except:
                            pass

                    # Link
                    link_elem = card.select_one('a.a-link-normal[href*="/dp/"]')
                    link = 'https://www.amazon.com.br' + link_elem.get('href', '') if link_elem else ''

                    if nome and preco and preco > 0:
                        produtos.append({
                            'nome': nome[:120],
                            'preco': preco,
                            'supermercado': 'Amazon',
                            'url': link,
                            'fonte': 'amazon',
                            'disponivel': True
                        })
                except:
                    continue

        except:
            pass

        return produtos

    def _buscar_americanas(self, termo: str) -> List[Dict]:
        """Busca nas Americanas"""
        produtos = []

        termo_formatado = quote_plus(termo)
        url = f"https://www.americanas.com.br/busca/{termo_formatado}"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Tentar extrair dados JSON embutidos
            scripts = soup.select('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items[:15]:
                            produto = item.get('item', {})
                            nome = produto.get('name')
                            offers = produto.get('offers', {})
                            preco = offers.get('price') or offers.get('lowPrice')

                            if nome and preco:
                                produtos.append({
                                    'nome': nome[:120],
                                    'preco': float(preco),
                                    'supermercado': 'Americanas',
                                    'url': produto.get('url', url),
                                    'fonte': 'americanas',
                                    'disponivel': True
                                })
                except:
                    continue

            # Fallback: parsing HTML
            if not produtos:
                cards = soup.select('[class*="product-card"]') or soup.select('[class*="ProductCard"]')
                for card in cards[:15]:
                    try:
                        nome_elem = card.select_one('[class*="product-name"]') or card.select_one('h3')
                        preco_elem = card.select_one('[class*="price"]')

                        nome = nome_elem.get_text(strip=True) if nome_elem else None
                        preco_texto = preco_elem.get_text(strip=True) if preco_elem else None
                        preco = self._extrair_preco(preco_texto) if preco_texto else None

                        if nome and preco:
                            produtos.append({
                                'nome': nome[:120],
                                'preco': preco,
                                'supermercado': 'Americanas',
                                'url': url,
                                'fonte': 'americanas',
                                'disponivel': True
                            })
                    except:
                        continue

        except:
            pass

        return produtos

    def _buscar_magalu(self, termo: str) -> List[Dict]:
        """Busca na Magazine Luiza"""
        produtos = []

        termo_formatado = quote_plus(termo)
        url = f"https://www.magazineluiza.com.br/busca/{termo_formatado}/"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Dados JSON estruturados
            scripts = soup.select('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product':
                                nome = item.get('name')
                                offers = item.get('offers', {})
                                preco = offers.get('price') or offers.get('lowPrice')

                                if nome and preco:
                                    produtos.append({
                                        'nome': nome[:120],
                                        'preco': float(preco),
                                        'supermercado': 'Magazine Luiza',
                                        'url': item.get('url', url),
                                        'fonte': 'magalu',
                                        'disponivel': True
                                    })
                    elif isinstance(data, dict) and data.get('@type') == 'Product':
                        nome = data.get('name')
                        offers = data.get('offers', {})
                        preco = offers.get('price') or offers.get('lowPrice')

                        if nome and preco:
                            produtos.append({
                                'nome': nome[:120],
                                'preco': float(preco),
                                'supermercado': 'Magazine Luiza',
                                'url': data.get('url', url),
                                'fonte': 'magalu',
                                'disponivel': True
                            })
                except:
                    continue

            # Fallback HTML
            if not produtos:
                cards = soup.select('[data-testid="product-card"]')
                for card in cards[:15]:
                    try:
                        nome_elem = card.select_one('[data-testid="product-title"]')
                        preco_elem = card.select_one('[data-testid="price-value"]')

                        nome = nome_elem.get_text(strip=True) if nome_elem else None
                        preco_texto = preco_elem.get_text(strip=True) if preco_elem else None
                        preco = self._extrair_preco(preco_texto) if preco_texto else None

                        if nome and preco:
                            produtos.append({
                                'nome': nome[:120],
                                'preco': preco,
                                'supermercado': 'Magazine Luiza',
                                'url': url,
                                'fonte': 'magalu',
                                'disponivel': True
                            })
                    except:
                        continue

        except:
            pass

        return produtos

    def _buscar_casasbahia(self, termo: str) -> List[Dict]:
        """Busca nas Casas Bahia"""
        produtos = []

        termo_formatado = quote_plus(termo)
        url = f"https://www.casasbahia.com.br/busca/{termo_formatado}"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # JSON estruturado
            scripts = soup.select('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items[:15]:
                            produto = item.get('item', {})
                            nome = produto.get('name')
                            offers = produto.get('offers', {})
                            preco = offers.get('price') or offers.get('lowPrice')

                            if nome and preco:
                                produtos.append({
                                    'nome': nome[:120],
                                    'preco': float(preco),
                                    'supermercado': 'Casas Bahia',
                                    'url': produto.get('url', url),
                                    'fonte': 'casasbahia',
                                    'disponivel': True
                                })
                except:
                    continue

        except:
            pass

        return produtos

    def _buscar_carrefour(self, termo: str) -> List[Dict]:
        """Busca no Carrefour"""
        produtos = []

        termo_formatado = quote_plus(termo)
        url = f"https://www.carrefour.com.br/s?q={termo_formatado}"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # Tentar JSON estruturado
            scripts = soup.select('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') == 'Product':
                            nome = data.get('name')
                            offers = data.get('offers', {})
                            preco = offers.get('price') or offers.get('lowPrice')

                            if nome and preco:
                                produtos.append({
                                    'nome': nome[:120],
                                    'preco': float(preco),
                                    'supermercado': 'Carrefour',
                                    'url': data.get('url', url),
                                    'fonte': 'carrefour',
                                    'disponivel': True
                                })
                        elif data.get('@type') == 'ItemList':
                            items = data.get('itemListElement', [])
                            for item in items[:15]:
                                produto = item.get('item', {})
                                nome = produto.get('name')
                                offers = produto.get('offers', {})
                                preco = offers.get('price') or offers.get('lowPrice')

                                if nome and preco:
                                    produtos.append({
                                        'nome': nome[:120],
                                        'preco': float(preco),
                                        'supermercado': 'Carrefour',
                                        'url': produto.get('url', url),
                                        'fonte': 'carrefour',
                                        'disponivel': True
                                    })
                except:
                    continue

            # Fallback HTML
            if not produtos:
                cards = soup.select('[class*="product-card"]')
                for card in cards[:15]:
                    try:
                        nome_elem = card.select_one('[class*="product-name"]') or card.select_one('h3')
                        preco_elem = card.select_one('[class*="price"]')

                        nome = nome_elem.get_text(strip=True) if nome_elem else None
                        preco = self._extrair_preco(preco_elem.get_text(strip=True)) if preco_elem else None

                        if nome and preco:
                            produtos.append({
                                'nome': nome[:120],
                                'preco': preco,
                                'supermercado': 'Carrefour',
                                'url': url,
                                'fonte': 'carrefour',
                                'disponivel': True
                            })
                    except:
                        continue

        except:
            pass

        return produtos

    def _buscar_extra(self, termo: str) -> List[Dict]:
        """Busca no Extra"""
        produtos = []

        termo_formatado = quote_plus(termo)
        url = f"https://www.extra.com.br/busca/{termo_formatado}"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # JSON estruturado
            scripts = soup.select('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items[:15]:
                            produto = item.get('item', {})
                            nome = produto.get('name')
                            offers = produto.get('offers', {})
                            preco = offers.get('price') or offers.get('lowPrice')

                            if nome and preco:
                                produtos.append({
                                    'nome': nome[:120],
                                    'preco': float(preco),
                                    'supermercado': 'Extra',
                                    'url': produto.get('url', url),
                                    'fonte': 'extra',
                                    'disponivel': True
                                })
                except:
                    continue

        except:
            pass

        return produtos

    def _buscar_shopee(self, termo: str) -> List[Dict]:
        """Busca na Shopee"""
        produtos = []

        termo_formatado = quote_plus(termo)
        # Shopee usa API interna
        url = f"https://shopee.com.br/api/v4/search/search_items?keyword={termo_formatado}&limit=20"

        try:
            extra_headers = {
                'Accept': 'application/json',
                'Referer': f'https://shopee.com.br/search?keyword={termo_formatado}'
            }
            response = self._fazer_request(url, extra_headers=extra_headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                for item in items[:15]:
                    try:
                        item_basic = item.get('item_basic', {})
                        nome = item_basic.get('name')
                        preco = item_basic.get('price', 0) / 100000  # Shopee usa centavos * 1000

                        if nome and preco > 0:
                            produtos.append({
                                'nome': nome[:120],
                                'preco': preco,
                                'supermercado': 'Shopee',
                                'url': f"https://shopee.com.br/{nome.replace(' ', '-')}-i.{item_basic.get('shopid')}.{item_basic.get('itemid')}",
                                'fonte': 'shopee',
                                'disponivel': True
                            })
                    except:
                        continue

        except:
            # Fallback: busca HTML
            try:
                html_url = f"https://shopee.com.br/search?keyword={termo_formatado}"
                response = self._fazer_request(html_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    scripts = soup.select('script[type="application/ld+json"]')
                    for script in scripts:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, dict) and data.get('@type') == 'ItemList':
                                items = data.get('itemListElement', [])
                                for item in items[:15]:
                                    produto = item.get('item', {})
                                    nome = produto.get('name')
                                    offers = produto.get('offers', {})
                                    preco = offers.get('price')

                                    if nome and preco:
                                        produtos.append({
                                            'nome': nome[:120],
                                            'preco': float(preco),
                                            'supermercado': 'Shopee',
                                            'url': produto.get('url', html_url),
                                            'fonte': 'shopee',
                                            'disponivel': True
                                        })
                        except:
                            continue
            except:
                pass

        return produtos

    def _buscar_duckduckgo(self, termo: str) -> List[Dict]:
        """Busca no DuckDuckGo para encontrar precos em outras lojas"""
        produtos = []

        # Buscar com termos de compra
        queries = [
            f"{termo} preço comprar",
            f"{termo} menor preço brasil",
        ]

        for query in queries:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

            try:
                response = self._fazer_request(url)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                results = soup.select('.result')

                for result in results[:10]:
                    try:
                        titulo_elem = result.select_one('.result__title a')
                        titulo = titulo_elem.get_text(strip=True) if titulo_elem else None

                        snippet_elem = result.select_one('.result__snippet')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

                        link = titulo_elem.get('href', '') if titulo_elem else ''

                        # Extrair preco do texto
                        texto_completo = f"{titulo} {snippet}"
                        preco = self._extrair_preco(texto_completo)

                        # Identificar loja
                        loja = self._identificar_loja(link)

                        if titulo and preco and preco > 0 and preco < 50000:
                            produtos.append({
                                'nome': titulo[:120],
                                'preco': preco,
                                'supermercado': loja,
                                'url': link,
                                'fonte': 'duckduckgo',
                                'disponivel': True
                            })
                    except:
                        continue

            except:
                continue

            time.sleep(0.3)

        return produtos

    def _buscar_google_shopping(self, termo: str) -> List[Dict]:
        """Busca simulada do Google Shopping via DuckDuckGo"""
        produtos = []

        # Google Shopping via DuckDuckGo
        query = f"site:shopping.google.com.br {termo}"
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        try:
            response = self._fazer_request(url)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.select('.result')

            for result in results[:10]:
                try:
                    titulo_elem = result.select_one('.result__title a')
                    titulo = titulo_elem.get_text(strip=True) if titulo_elem else None

                    snippet_elem = result.select_one('.result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

                    link = titulo_elem.get('href', '') if titulo_elem else ''

                    # Extrair preco
                    texto_completo = f"{titulo} {snippet}"
                    preco = self._extrair_preco(texto_completo)

                    if titulo and preco and preco > 0 and preco < 50000:
                        produtos.append({
                            'nome': titulo[:120],
                            'preco': preco,
                            'supermercado': 'Google Shopping',
                            'url': link,
                            'fonte': 'google_shopping',
                            'disponivel': True
                        })
                except:
                    continue

        except:
            pass

        return produtos

    def _extrair_preco(self, texto: str) -> Optional[float]:
        """Extrai valor numerico de texto de preco"""
        if not texto:
            return None

        # Limpar texto
        texto = texto.replace('\xa0', ' ').strip()

        # Padroes de preco brasileiro: R$ 1.234,56
        padroes = [
            r'R\$\s*([\d.]+),(\d{2})',      # R$ 1.234,56
            r'R\$\s*([\d]+),(\d{2})',        # R$ 1234,56
            r'([\d.]+),(\d{2})\s*(?:reais|R\$)', # 1.234,56 reais
            r'([\d.]+),(\d{2})',              # 1.234,56
            r'([\d]+),(\d{2})',               # 1234,56
            r'R\$\s*([\d.]+)',                # R$ 1234 (sem centavos)
            r'([\d]+)\s*(?:reais|R\$)',       # 1234 reais
        ]

        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                grupos = match.groups()
                try:
                    if len(grupos) == 2:
                        inteiro = grupos[0].replace('.', '')
                        decimal = grupos[1]
                        return float(f"{inteiro}.{decimal}")
                    elif len(grupos) == 1:
                        return float(grupos[0].replace('.', ''))
                except:
                    continue

        return None

    def _identificar_loja(self, url: str) -> str:
        """Identifica a loja pela URL"""
        url_lower = url.lower()

        lojas = {
            'mercadolivre': 'Mercado Livre',
            'amazon': 'Amazon',
            'americanas': 'Americanas',
            'magazineluiza': 'Magazine Luiza',
            'magalu': 'Magazine Luiza',
            'casasbahia': 'Casas Bahia',
            'extra.com': 'Extra',
            'carrefour': 'Carrefour',
            'paodeacucar': 'Pao de Acucar',
            'shopee': 'Shopee',
            'kabum': 'Kabum',
            'zoom.com': 'Zoom',
            'buscape': 'Buscape',
            'pontofrio': 'Ponto Frio',
            'walmart': 'Walmart',
            'fastshop': 'Fast Shop',
            'submarino': 'Submarino',
            'netshoes': 'Netshoes',
            'centauro': 'Centauro',
            'dafiti': 'Dafiti',
            'aliexpress': 'AliExpress',
            'mercadolibre': 'Mercado Livre',
        }

        for chave, nome in lojas.items():
            if chave in url_lower:
                return nome

        return 'Loja Online'

    def _remover_duplicatas(self, produtos: List[Dict]) -> List[Dict]:
        """Remove produtos duplicados baseado em nome similar e preco"""
        if not produtos:
            return []

        vistos = {}
        unicos = []

        for p in produtos:
            # Criar chave normalizada
            nome_normalizado = re.sub(r'[^\w\s]', '', p.get('nome', '').lower())[:40]
            preco = p.get('preco', 0)

            # Chave unica: nome + faixa de preco (10%)
            chave = f"{nome_normalizado}_{int(preco / max(preco * 0.1, 1))}"

            if chave not in vistos:
                vistos[chave] = True
                unicos.append(p)

        return unicos


# Instancia global
buscador_precos_reais = BuscadorPrecosReais()


def buscar_precos_reais(termo: str, limite: int = 20) -> List[Dict]:
    """Funcao auxiliar para buscar precos reais"""
    return buscador_precos_reais.buscar(termo, limite)


# Teste
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTE DE BUSCA DE PRECOS REAIS")
    print("="*60)

    termo_teste = "arroz 5kg"
    resultados = buscar_precos_reais(termo_teste, limite=30)

    print(f"\n📊 Resultados para '{termo_teste}':\n")
    for i, r in enumerate(resultados, 1):
        print(f"{i:2}. R$ {r['preco']:8.2f} | {r['supermercado']:15} | {r['nome'][:50]}")

    print(f"\n✅ Total: {len(resultados)} produtos reais encontrados")
