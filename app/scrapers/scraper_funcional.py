"""
Scraper Funcional - Estratégias que REALMENTE funcionam
Baseado em testes práticos
"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json


class ScraperFuncional:
    """Scraper testado e funcional"""

    def __init__(self):
        self.session = requests.Session()
        # User agent mais realista
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _clean_price(self, price_str: str) -> float:
        """Limpa string de preço"""
        try:
            if isinstance(price_str, (int, float)):
                return float(price_str)
            # Remover tudo exceto dígitos, vírgula e ponto
            price_str = re.sub(r'[^\d,.]', '', str(price_str))
            # Se tem vírgula e ponto, remover ponto (separador de milhar)
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '')
            # Converter vírgula para ponto
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0

    def buscar_mercadolivre_html(self, termo: str) -> List[Dict]:
        """
        Busca no Mercado Livre via HTML (funciona!)
        """
        produtos = []

        try:
            # URL de busca
            termo_url = termo.replace(' ', '-')
            url = f"https://lista.mercadolivre.com.br/{termo_url}"

            print(f"   🔍 Mercado Livre (HTML): {termo}")

            # Headers específicos para ML
            headers = {
                **self.session.headers,
                'Referer': 'https://www.mercadolivre.com.br/',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
            }

            time.sleep(random.uniform(1, 2))

            response = self.session.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Procurar por produtos
                # Mercado Livre usa diferentes estruturas
                items = soup.find_all('li', class_='ui-search-layout__item')

                if not items:
                    # Tentar outro seletor
                    items = soup.find_all('div', class_='ui-search-result__wrapper')

                print(f"   ✓ Encontrados {len(items)} cards de produtos")

                for item in items[:15]:
                    try:
                        # Nome do produto
                        nome_elem = item.find('h2', class_='ui-search-item__title')
                        if not nome_elem:
                            nome_elem = item.find('a', class_='ui-search-item__group__element')

                        if not nome_elem:
                            continue

                        nome = nome_elem.get_text(strip=True)

                        # Preço
                        preco_elem = item.find('span', class_='andes-money-amount__fraction')
                        if not preco_elem:
                            preco_elem = item.find('span', class_='price-tag-fraction')

                        if not preco_elem:
                            continue

                        preco_text = preco_elem.get_text(strip=True)
                        preco = self._clean_price(preco_text)

                        if preco == 0:
                            continue

                        # URL
                        url_elem = item.find('a', href=True)
                        url_produto = url_elem['href'] if url_elem else ''

                        # Verificar se tem desconto
                        desconto_elem = item.find('span', class_='ui-search-price__discount')
                        em_promocao = desconto_elem is not None

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': em_promocao,
                            'url': url_produto,
                            'supermercado': 'Mercado Livre',
                            'disponivel': True
                        })

                    except Exception as e:
                        continue

                print(f"   ✅ Mercado Livre: {len(produtos)} produtos extraídos")
            else:
                print(f"   ❌ Status {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro Mercado Livre: {e}")

        return produtos

    def buscar_google_shopping(self, termo: str) -> List[Dict]:
        """
        Busca no Google Shopping (funciona bem!)
        """
        produtos = []

        try:
            # Google Shopping URL
            url = "https://www.google.com/search"

            params = {
                'q': termo,
                'tbm': 'shop',
                'hl': 'pt-BR',
                'gl': 'br'
            }

            print(f"   🔍 Google Shopping: {termo}")

            headers = {
                **self.session.headers,
                'Referer': 'https://www.google.com/'
            }

            time.sleep(random.uniform(1, 2))

            response = self.session.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Google Shopping tem estrutura específica
                items = soup.find_all('div', class_='sh-dgr__content')

                if not items:
                    # Tentar outra estrutura
                    items = soup.find_all('div', {'data-sh-product': True})

                print(f"   ✓ Encontrados {len(items)} produtos")

                for item in items[:15]:
                    try:
                        # Nome
                        nome_elem = item.find('h3') or item.find('h4')
                        if not nome_elem:
                            continue
                        nome = nome_elem.get_text(strip=True)

                        # Preço
                        preco_elem = item.find('span', class_='a8Pemb')
                        if not preco_elem:
                            preco_elem = item.find('b')

                        if not preco_elem:
                            continue

                        preco_text = preco_elem.get_text(strip=True)
                        preco = self._clean_price(preco_text)

                        if preco == 0:
                            continue

                        # Loja
                        loja_elem = item.find('div', class_='aULzUe')
                        loja = loja_elem.get_text(strip=True) if loja_elem else 'Google Shopping'

                        # URL
                        url_elem = item.find('a', href=True)
                        url_produto = url_elem['href'] if url_elem else ''

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': False,
                            'url': url_produto,
                            'supermercado': loja,
                            'disponivel': True
                        })

                    except Exception as e:
                        continue

                print(f"   ✅ Google Shopping: {len(produtos)} produtos")
            else:
                print(f"   ❌ Status {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro Google Shopping: {e}")

        return produtos

    def buscar_buscape(self, termo: str) -> List[Dict]:
        """
        Busca no Buscapé (comparador de preços)
        """
        produtos = []

        try:
            url = f"https://www.buscape.com.br/search/{termo}"

            print(f"   🔍 Buscapé: {termo}")

            time.sleep(random.uniform(1, 2))

            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscapé tem cards de produtos
                items = soup.find_all('div', class_='ProductCard_ProductCard_Inner__gapf0')

                print(f"   ✓ Encontrados {len(items)} produtos")

                for item in items[:15]:
                    try:
                        # Nome
                        nome_elem = item.find('h2')
                        if not nome_elem:
                            continue
                        nome = nome_elem.get_text(strip=True)

                        # Preço
                        preco_elem = item.find('p', {'data-testid': 'product-card::price'})
                        if not preco_elem:
                            continue

                        preco_text = preco_elem.get_text(strip=True)
                        preco = self._clean_price(preco_text)

                        if preco == 0:
                            continue

                        # URL
                        url_elem = item.find('a', href=True)
                        url_produto = url_elem['href'] if url_elem else ''
                        if url_produto and not url_produto.startswith('http'):
                            url_produto = f"https://www.buscape.com.br{url_produto}"

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': False,
                            'url': url_produto,
                            'supermercado': 'Buscapé',
                            'disponivel': True
                        })

                    except Exception as e:
                        continue

                print(f"   ✅ Buscapé: {len(produtos)} produtos")
            else:
                print(f"   ❌ Status {response.status_code}")

        except Exception as e:
            print(f"   ❌ Erro Buscapé: {e}")

        return produtos

    def buscar_todos(self, termo: str) -> List[Dict]:
        """Busca em todas as fontes funcionais"""
        print(f"\n{'='*60}")
        print(f"🔍 SCRAPER FUNCIONAL: '{termo}'")
        print(f"{'='*60}")

        todos_produtos = []

        # Fontes testadas e funcionais
        fontes = [
            self.buscar_mercadolivre_html,
            self.buscar_google_shopping,
            self.buscar_buscape,
        ]

        for metodo in fontes:
            try:
                produtos = metodo(termo)
                todos_produtos.extend(produtos)

                # Delay entre fontes
                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"   ❌ Erro: {e}")

        # Remover duplicatas
        produtos_unicos = {}
        for p in todos_produtos:
            key = f"{p['nome'][:40].lower()}_{p['preco']:.2f}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        resultado = list(produtos_unicos.values())

        print(f"\n{'='*60}")
        print(f"✅ TOTAL: {len(resultado)} produtos únicos")
        print(f"{'='*60}\n")

        return resultado


# Instância global
scraper_funcional = ScraperFuncional()
