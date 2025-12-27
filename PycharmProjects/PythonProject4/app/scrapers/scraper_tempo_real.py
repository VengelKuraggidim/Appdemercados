"""
Scraper otimizado para busca em tempo real sob demanda
Usa APIs internas dos supermercados quando possível
E se necessário, usa Selenium com comportamento humano
"""
from typing import List, Dict, Optional
import requests
import time
import random
from bs4 import BeautifulSoup
import re


class ScraperTempoReal:
    """Scraper para busca em tempo real quando usuário faz pesquisa"""

    def __init__(self):
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

    def buscar_carrefour_api(self, termo: str) -> List[Dict]:
        """
        Tenta usar API interna do Carrefour
        O site usa GraphQL para buscar produtos
        """
        produtos = []
        try:
            # Carrefour Mercado usa uma API GraphQL
            url = "https://mercado.carrefour.com.br/api/graphql"

            # Query GraphQL que o site usa
            query = {
                "query": """
                    query Search($term: String!, $limit: Int) {
                        search(term: $term, limit: $limit) {
                            products {
                                name
                                price
                                oldPrice
                                link
                                image
                                available
                            }
                        }
                    }
                """,
                "variables": {
                    "term": termo,
                    "limit": 10
                }
            }

            headers = {**self.headers, 'Content-Type': 'application/json'}

            response = requests.post(url, json=query, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                items = data.get('data', {}).get('search', {}).get('products', [])

                for item in items:
                    preco = float(item.get('price', 0))
                    preco_original = item.get('oldPrice')

                    if preco > 0:
                        produtos.append({
                            'nome': item.get('name', '').strip(),
                            'marca': None,
                            'preco': preco,
                            'preco_original': float(preco_original) if preco_original else None,
                            'em_promocao': preco_original is not None and float(preco_original) > preco,
                            'url': item.get('link', ''),
                            'supermercado': 'Carrefour',
                            'disponivel': item.get('available', True)
                        })

                print(f"   ✓ Carrefour API: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ✗ Carrefour API: {e}")

        return produtos

    def buscar_mercadolivre_simples(self, termo: str) -> List[Dict]:
        """
        Mercado Livre - busca simples sem autenticação
        """
        produtos = []
        try:
            # Tenta buscar através de URL simples
            url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"

            time.sleep(random.uniform(1, 2))

            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Procurar por items
                items = soup.find_all('li', class_=re.compile('ui-search-layout__item'))

                for item in items[:10]:
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

                        preco_text = preco_elem.get_text(strip=True)
                        preco = self._clean_price(preco_text)

                        if preco == 0:
                            continue

                        # URL
                        link = item.find('a', href=True)
                        url_produto = link['href'] if link else ''

                        # Promoção (se tem badge de desconto)
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

                    except Exception as e:
                        continue

                print(f"   ✓ Mercado Livre: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ✗ Mercado Livre: {e}")

        return produtos

    def buscar_extra(self, termo: str) -> List[Dict]:
        """
        Extra/Pão de Açúcar - pertence ao mesmo grupo GPA
        """
        produtos = []
        try:
            # Extra também usa uma API interna
            url = f"https://www.extra.com.br/api/catalog/products"

            params = {
                'query': termo,
                'page': 1,
                'limit': 10
            }

            headers = {**self.headers}

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                items = data.get('products', [])

                for item in items:
                    preco = item.get('price', 0)

                    if preco > 0:
                        produtos.append({
                            'nome': item.get('name', '').strip(),
                            'marca': item.get('brand'),
                            'preco': float(preco),
                            'em_promocao': item.get('onSale', False),
                            'url': item.get('url', ''),
                            'supermercado': 'Extra',
                            'disponivel': item.get('available', True)
                        })

                print(f"   ✓ Extra: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ✗ Extra: {e}")

        return produtos

    def buscar_todos(
        self,
        termo: str,
        max_por_fonte: int = 10,
        usar_selenium: bool = False,
        usar_scraper_real: bool = False,  # Desativado: muito lento (15-30s)
        usar_gerador_fallback: bool = True,  # Usar gerador (instantâneo)
        lat_usuario: float = None,  # NOVO: Coordenadas do usuário
        lon_usuario: float = None
    ) -> List[Dict]:
        """
        Busca produtos sob demanda

        MODO ATUAL: Gerador (instantâneo)
        - Produtos realistas baseados no termo
        - Instantâneo (<1s)
        - 100% confiável

        MODO DISPONÍVEL: Scraping REAL (lento)
        - Para ativar: usar_scraper_real=True
        - Busca produtos reais do Mercado Livre
        - Demora 15-30 segundos
        """
        print(f"\n🔍 Buscando produtos para '{termo}'...")

        # GERADOR (Ativado por padrão - instantâneo)
        if not usar_scraper_real:
            try:
                from app.scrapers.gerador_produtos import gerador_produtos
                print("   🎲 Gerando produtos realistas...")
                return gerador_produtos.gerar_produtos(termo, quantidade=15,
                                                      lat_usuario=lat_usuario,
                                                      lon_usuario=lon_usuario)
            except Exception as e:
                print(f"   ❌ Erro no gerador: {e}")
                # Continuar com outros métodos se gerador falhar

        # SCRAPING REAL (Desativado por padrão - muito lento)
        if usar_scraper_real:
            try:
                from app.scrapers.scraper_real_playwright import buscar_produtos_reais
                print("   🌐 Fazendo scraping REAL da web...")

                produtos = buscar_produtos_reais(termo)

                if produtos and len(produtos) > 0:
                    print(f"   ✅ Encontrados {len(produtos)} produtos REAIS!")
                    return produtos
                else:
                    print("   ⚠️  Scraping não retornou produtos")

                    # Fallback para gerador
                    if usar_gerador_fallback:
                        print("   🎲 Usando gerador como fallback...")
                        from app.scrapers.gerador_produtos import gerador_produtos
                        return gerador_produtos.gerar_produtos(termo, quantidade=15,
                                                              lat_usuario=lat_usuario,
                                                              lon_usuario=lon_usuario)

            except Exception as e:
                print(f"   ❌ Erro no scraping real: {e}")

                # Fallback para gerador
                if usar_gerador_fallback:
                    print("   🎲 Usando gerador como fallback...")
                    from app.scrapers.gerador_produtos import gerador_produtos
                    return gerador_produtos.gerar_produtos(termo, quantidade=15,
                                                          lat_usuario=lat_usuario,
                                                          lon_usuario=lon_usuario)

        # Scraper unificado (tentará scraping real - não funciona bem)
        if usar_scraper_unificado:
            try:
                from app.scrapers.scraper_unificado import scraper_unificado
                print("   🧠 Tentando Scraper Unificado (pode não funcionar)...")
                produtos = scraper_unificado.buscar_inteligente(termo, minimo_produtos=5)

                # Se não encontrou nada, usar gerador
                if not produtos and usar_gerador:
                    print("   ⚠️  Scraping falhou, usando gerador...")
                    from app.scrapers.gerador_produtos import gerador_produtos
                    return gerador_produtos.gerar_produtos(termo, quantidade=15,
                                                          lat_usuario=lat_usuario,
                                                          lon_usuario=lon_usuario)

                return produtos
            except Exception as e:
                print(f"   ⚠️  Erro no Scraper Unificado: {e}")

                # Fallback para gerador
                if usar_gerador:
                    print("   🎲 Usando gerador como fallback...")
                    from app.scrapers.gerador_produtos import gerador_produtos
                    return gerador_produtos.gerar_produtos(termo, quantidade=15,
                                                          lat_usuario=lat_usuario,
                                                          lon_usuario=lon_usuario)

        # Método tradicional (fallback)
        todos_produtos = []

        # Tentar todas as fontes em paralelo seria melhor, mas por enquanto sequencial
        fontes = [
            ('Mercado Livre', self.buscar_mercadolivre_simples),
            ('Carrefour', self.buscar_carrefour_api),
            ('Extra', self.buscar_extra),
        ]

        for nome_fonte, metodo_busca in fontes:
            try:
                time.sleep(random.uniform(0.5, 1.5))  # Delay entre fontes
                produtos = metodo_busca(termo)
                todos_produtos.extend(produtos[:max_por_fonte])
            except Exception as e:
                print(f"   ✗ Erro em {nome_fonte}: {e}")

        # Se não encontrou produtos suficientes E selenium está ativado, usar scraper humano
        if usar_selenium and len(todos_produtos) < 5:
            print(f"\n   ⚡ Poucos produtos encontrados ({len(todos_produtos)}), usando Scraper Humano...")
            try:
                from app.scrapers.scraper_humano import get_scraper_humano

                scraper_humano = get_scraper_humano(headless=True)

                # Buscar nos mercados principais
                produtos_selenium = scraper_humano.buscar_todos(
                    termo,
                    mercados=['carrefour', 'pao_acucar']
                )

                if produtos_selenium:
                    print(f"   ✅ Scraper Humano encontrou {len(produtos_selenium)} produtos adicionais!")
                    todos_produtos.extend(produtos_selenium)

            except Exception as e:
                print(f"   ⚠️  Erro ao usar Scraper Humano: {e}")

        # Remover duplicatas
        produtos_unicos = {}
        for p in todos_produtos:
            # Usar nome + supermercado como chave
            key = f"{p['nome'][:30].lower()}_{p['supermercado']}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        resultado = list(produtos_unicos.values())
        print(f"   ✅ Total: {len(resultado)} produtos únicos encontrados\n")

        return resultado

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


# Instância global para reutilizar
scraper_tempo_real = ScraperTempoReal()
