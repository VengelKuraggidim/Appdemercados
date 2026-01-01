"""
Scraper simples usando apenas requests + BeautifulSoup
Funciona em qualquer ambiente, sem necessidade de Chrome/ChromeDriver
"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
import random
import re


class ScraperSimples:
    """Scraper leve sem dependência de Selenium"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })

    def _clean_price(self, price_str: str) -> float:
        """Limpa string de preço"""
        try:
            price_str = re.sub(r'[^\d,.]', '', price_str)
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '')
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0

    def buscar_mercadolivre(self, termo: str) -> List[Dict]:
        """Busca no Mercado Livre"""
        produtos = []

        try:
            url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
            print(f"   🔍 Mercado Livre: {termo}")

            time.sleep(random.uniform(1, 2))

            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar cards de produtos
                items = soup.find_all('li', class_=re.compile('ui-search-layout__item'))

                for item in items[:15]:
                    try:
                        # Nome
                        nome_elem = item.find('h2', class_=re.compile('ui-search-item__title'))
                        if not nome_elem:
                            continue
                        nome = nome_elem.get_text(strip=True)

                        # Preço
                        preco_elem = item.find('span', class_=re.compile('andes-money-amount__fraction'))
                        if not preco_elem:
                            continue

                        preco = self._clean_price(preco_elem.get_text(strip=True))
                        if preco == 0:
                            continue

                        # URL
                        link = item.find('a', href=True)
                        url_produto = link['href'] if link else ''

                        # Promoção
                        em_promocao = item.find(class_=re.compile('ui-search-price__discount')) is not None

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': em_promocao,
                            'url': url_produto,
                            'supermercado': 'Mercado Livre',
                            'disponivel': True
                        })

                    except Exception:
                        continue

                print(f"   ✅ Mercado Livre: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Mercado Livre: {e}")

        return produtos

    def buscar_americanas(self, termo: str) -> List[Dict]:
        """Busca nas Americanas"""
        produtos = []

        try:
            url = f"https://www.americanas.com.br/busca/{termo.replace(' ', '-')}"
            print(f"   🔍 Americanas: {termo}")

            time.sleep(random.uniform(1, 2))

            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar produtos (seletores podem mudar)
                items = soup.find_all('div', class_=re.compile('product|Product'))

                for item in items[:15]:
                    try:
                        # Nome
                        nome = None
                        for tag in ['h2', 'h3', 'span', 'a']:
                            elem = item.find(tag, class_=re.compile('name|title|Title'))
                            if elem:
                                nome = elem.get_text(strip=True)
                                if len(nome) > 3:
                                    break

                        if not nome:
                            continue

                        # Preço
                        preco = 0.0
                        for tag in ['span', 'div', 'p']:
                            elem = item.find(tag, class_=re.compile('price|Price'))
                            if elem:
                                preco = self._clean_price(elem.get_text(strip=True))
                                if preco > 0:
                                    break

                        if preco == 0:
                            continue

                        # URL
                        link = item.find('a', href=True)
                        url_produto = link['href'] if link else ''
                        if url_produto and not url_produto.startswith('http'):
                            url_produto = f"https://www.americanas.com.br{url_produto}"

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': False,
                            'url': url_produto,
                            'supermercado': 'Americanas',
                            'disponivel': True
                        })

                    except Exception:
                        continue

                print(f"   ✅ Americanas: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Americanas: {e}")

        return produtos

    def buscar_todos(self, termo: str) -> List[Dict]:
        """Busca em todas as fontes disponíveis"""
        print(f"\n{'='*60}")
        print(f"🔍 BUSCANDO (Modo Simples): '{termo}'")
        print(f"{'='*60}")

        todos_produtos = []

        # Mercado Livre
        produtos_ml = self.buscar_mercadolivre(termo)
        todos_produtos.extend(produtos_ml)

        time.sleep(random.uniform(2, 3))

        # Americanas
        produtos_am = self.buscar_americanas(termo)
        todos_produtos.extend(produtos_am)

        # Remover duplicatas
        produtos_unicos = {}
        for p in todos_produtos:
            key = f"{p['nome'][:40].lower()}_{p['supermercado']}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        resultado = list(produtos_unicos.values())

        print(f"\n{'='*60}")
        print(f"✅ TOTAL: {len(resultado)} produtos encontrados")
        print(f"{'='*60}\n")

        return resultado


# Instância global
scraper_simples = ScraperSimples()
