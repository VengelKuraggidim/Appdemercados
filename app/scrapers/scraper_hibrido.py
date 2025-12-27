"""
Scraper híbrido que combina diferentes técnicas para buscar preços reais
"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time
import random
import json


class ScraperHibrido:
    """Scraper que tenta múltiplas fontes para encontrar preços reais"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def buscar_precos_google_shopping(self, termo: str) -> List[Dict]:
        """
        Busca preços através da busca do Google Shopping
        Esta é uma fonte mais acessível que retorna resultados de múltiplos varejistas
        """
        produtos = []

        try:
            # Busca no Google Shopping (versão simplificada)
            url = f"https://www.google.com/search?tbm=shop&q={termo}+supermercado+brasil"

            time.sleep(random.uniform(2, 4))
            response = self.session.get(url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Google Shopping usa divs específicas para produtos
                product_divs = soup.find_all('div', {'class': lambda x: x and 'sh-dgr__content' in str(x)})

                for div in product_divs[:10]:
                    try:
                        # Nome do produto
                        nome_elem = div.find(['h3', 'h4'])
                        if not nome_elem:
                            continue
                        nome = nome_elem.text.strip()

                        # Preço
                        preco_elem = div.find('span', {'class': lambda x: x and 'price' in str(x).lower()})
                        if not preco_elem:
                            preco_elem = div.find('b')

                        if not preco_elem:
                            continue

                        preco_text = preco_elem.text.strip()
                        preco = self._clean_price(preco_text)

                        if preco == 0:
                            continue

                        # Vendedor (supermercado)
                        vendedor_elem = div.find('div', {'class': lambda x: x and 'merchant' in str(x).lower()})
                        supermercado = vendedor_elem.text.strip() if vendedor_elem else "Google Shopping"

                        # Link
                        link_elem = div.find('a', href=True)
                        url = link_elem['href'] if link_elem else ""

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': False,
                            'url': url,
                            'supermercado': supermercado,
                            'disponivel': True
                        })

                    except Exception as e:
                        continue

                print(f"   Google Shopping: {len(produtos)} produtos")

        except Exception as e:
            print(f"   Erro Google Shopping: {e}")

        return produtos

    def buscar_comparadores(self, termo: str) -> List[Dict]:
        """
        Busca em sites comparadores de preço brasileiros
        Exemplos: Zoom, Buscapé, etc
        """
        produtos = []

        try:
            # Buscapé API (endpoint público de busca)
            url = f"https://www.buscape.com.br/search?q={termo}"

            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscapé tem estrutura específica
                cards = soup.find_all(['div', 'article'], {'class': lambda x: x and 'Card' in str(x)})

                for card in cards[:10]:
                    try:
                        nome_elem = card.find(['h2', 'h3', 'a'])
                        if not nome_elem:
                            continue
                        nome = nome_elem.text.strip()

                        preco_elem = card.find('p', {'class': lambda x: x and 'price' in str(x).lower()})
                        if not preco_elem:
                            continue

                        preco = self._clean_price(preco_elem.text)
                        if preco == 0:
                            continue

                        link_elem = card.find('a', href=True)
                        url = link_elem['href'] if link_elem else ""

                        produtos.append({
                            'nome': nome,
                            'marca': None,
                            'preco': preco,
                            'em_promocao': False,
                            'url': url,
                            'supermercado': "Buscapé",
                            'disponivel': True
                        })

                    except:
                        continue

                print(f"   Buscapé: {len(produtos)} produtos")

        except Exception as e:
            print(f"   Erro Buscapé: {e}")

        return produtos

    def search(self, termo: str) -> List[Dict]:
        """
        Busca produtos combinando múltiplas fontes
        """
        print(f"\n🔍 Buscando '{termo}' em múltiplas fontes...")

        todos_produtos = []

        # Tentar Google Shopping
        produtos_google = self.buscar_precos_google_shopping(termo)
        todos_produtos.extend(produtos_google)

        # Tentar comparadores
        if len(todos_produtos) < 5:
            produtos_comparadores = self.buscar_comparadores(termo)
            todos_produtos.extend(produtos_comparadores)

        # Remover duplicatas por nome
        produtos_unicos = {}
        for p in todos_produtos:
            nome_key = p['nome'].lower()[:50]
            if nome_key not in produtos_unicos:
                produtos_unicos[nome_key] = p

        resultado = list(produtos_unicos.values())[:20]
        print(f"   ✓ Total: {len(resultado)} produtos únicos")

        return resultado

    def _clean_price(self, price_str: str) -> float:
        """Limpa e converte string de preço para float"""
        try:
            import re
            # Remover tudo exceto dígitos, vírgula e ponto
            price_str = re.sub(r'[^\d,.]', '', price_str)
            # Se tiver ponto e vírgula, remover ponto (separador de milhares)
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '')
            # Converter vírgula para ponto
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0
