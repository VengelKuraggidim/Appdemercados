"""
Scraper moderno usando Playwright
Mais eficiente e menos detectável que Selenium
"""
from typing import List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random
import re


class ScraperPlaywright:
    """Scraper usando Playwright com técnicas anti-detecção"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def _init_browser(self):
        """Inicializa navegador Playwright"""
        if self.browser:
            return

        self.playwright = sync_playwright().start()

        # Usar Chromium com configurações anti-detecção
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )

        # Criar contexto com configurações realistas
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
            geolocation={'latitude': -23.5505, 'longitude': -46.6333},
            permissions=['geolocation']
        )

        # Adicionar script para remover webdriver
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
        """)

        print("   ✓ Playwright browser inicializado")

    def _clean_price(self, price_str: str) -> float:
        """Limpa e converte string de preço"""
        try:
            price_str = re.sub(r'[^\d,.]', '', price_str)
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '')
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0

    def _esperar_humano(self, min_sec: float = 1, max_sec: float = 3):
        """Delay aleatório"""
        time.sleep(random.uniform(min_sec, max_sec))

    def buscar_mercadolivre(self, termo: str) -> List[Dict]:
        """Busca no Mercado Livre usando Playwright"""
        produtos = []

        try:
            self._init_browser()
            page = self.context.new_page()

            url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
            print(f"   🔍 Mercado Livre (Playwright): {termo}")

            # Navegar
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            self._esperar_humano(2, 4)

            # Scroll suave
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            self._esperar_humano(1, 2)

            # Buscar produtos
            items = page.locator('li.ui-search-layout__item').all()
            print(f"   ✓ Encontrados {len(items)} itens")

            for i, item in enumerate(items[:15]):
                try:
                    # Nome
                    nome_elem = item.locator('h2.ui-search-item__title')
                    if nome_elem.count() == 0:
                        continue
                    nome = nome_elem.first.inner_text()

                    # Preço
                    preco_elem = item.locator('span.andes-money-amount__fraction')
                    if preco_elem.count() == 0:
                        continue
                    preco_text = preco_elem.first.inner_text()
                    preco = self._clean_price(preco_text)

                    if preco == 0:
                        continue

                    # URL
                    link_elem = item.locator('a').first
                    url_produto = link_elem.get_attribute('href') if link_elem else ''

                    # Promoção
                    em_promocao = item.locator('.ui-search-price__discount').count() > 0

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

            page.close()
            print(f"   ✅ Mercado Livre: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Mercado Livre: {e}")

        return produtos

    def buscar_carrefour(self, termo: str) -> List[Dict]:
        """Busca no Carrefour usando Playwright"""
        produtos = []

        try:
            self._init_browser()
            page = self.context.new_page()

            url = f"https://mercado.carrefour.com.br/busca?q={termo}"
            print(f"   🔍 Carrefour (Playwright): {termo}")

            page.goto(url, wait_until='networkidle', timeout=30000)
            self._esperar_humano(3, 5)

            # Scroll
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            self._esperar_humano(1, 2)

            # Tentar diferentes seletores
            selectors = [
                'div[data-testid="product-card"]',
                'div[class*="ProductCard"]',
                'article[class*="product"]'
            ]

            items = []
            for selector in selectors:
                items = page.locator(selector).all()
                if len(items) > 0:
                    print(f"   ✓ Encontrados {len(items)} produtos com '{selector}'")
                    break

            for item in items[:15]:
                try:
                    # Nome
                    nome = None
                    for tag in ['h2', 'h3', 'h4']:
                        try:
                            nome_elem = item.locator(tag).first
                            nome = nome_elem.inner_text()
                            if nome and len(nome) > 3:
                                break
                        except:
                            continue

                    if not nome:
                        continue

                    # Preço
                    preco = 0.0
                    price_selectors = [
                        'span[class*="price"]',
                        'div[class*="price"]',
                        'span[data-testid*="price"]'
                    ]

                    for ps in price_selectors:
                        try:
                            price_elem = item.locator(ps).first
                            preco_text = price_elem.inner_text()
                            preco = self._clean_price(preco_text)
                            if preco > 0:
                                break
                        except:
                            continue

                    if preco == 0:
                        continue

                    # URL
                    url_produto = ""
                    try:
                        link = item.locator('a').first
                        url_produto = link.get_attribute('href') or ""
                    except:
                        pass

                    produtos.append({
                        'nome': nome,
                        'marca': None,
                        'preco': preco,
                        'em_promocao': False,
                        'url': url_produto,
                        'supermercado': 'Carrefour',
                        'disponivel': True
                    })

                except Exception as e:
                    continue

            page.close()
            print(f"   ✅ Carrefour: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ❌ Erro Carrefour: {e}")

        return produtos

    def buscar_todos(self, termo: str, mercados: List[str] = None) -> List[Dict]:
        """Busca em todos os mercados"""
        print(f"\n{'='*60}")
        print(f"🎭 PLAYWRIGHT SCRAPER: '{termo}'")
        print(f"{'='*60}")

        mercados_disponiveis = {
            'mercadolivre': self.buscar_mercadolivre,
            'carrefour': self.buscar_carrefour,
        }

        if mercados:
            mercados_busca = {k: v for k, v in mercados_disponiveis.items() if k in mercados}
        else:
            mercados_busca = mercados_disponiveis

        todos_produtos = []

        for nome_mercado, metodo_busca in mercados_busca.items():
            try:
                produtos = metodo_busca(termo)
                todos_produtos.extend(produtos)

                if nome_mercado != list(mercados_busca.keys())[-1]:
                    self._esperar_humano(2, 4)

            except Exception as e:
                print(f"   ❌ Erro em {nome_mercado}: {e}")

        # Remover duplicatas
        produtos_unicos = {}
        for p in todos_produtos:
            key = f"{p['nome'][:40].lower()}_{p['supermercado']}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        resultado = list(produtos_unicos.values())

        print(f"\n{'='*60}")
        print(f"✅ TOTAL: {len(resultado)} produtos únicos")
        print(f"{'='*60}\n")

        return resultado

    def close(self):
        """Fecha browser"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def __del__(self):
        """Destrutor"""
        self.close()


# Instância global
_scraper_playwright_instance = None

def get_scraper_playwright(headless: bool = True) -> ScraperPlaywright:
    """Retorna instância global"""
    global _scraper_playwright_instance
    if _scraper_playwright_instance is None:
        _scraper_playwright_instance = ScraperPlaywright(headless=headless)
    return _scraper_playwright_instance
