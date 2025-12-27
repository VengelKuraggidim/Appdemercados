"""
Scraper Avançado que Simula Comportamento Humano
Usa Playwright com técnicas anti-detecção para supermercados brasileiros
"""
import asyncio
import random
import time
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import re


class ScraperHumanoAvancado:
    """
    Scraper que simula comportamento humano real
    Técnicas anti-detecção:
    - User agents reais e rotativos
    - Delays aleatórios entre ações
    - Movimentos de mouse simulados
    - Scrolling natural
    - Headers completos de navegador real
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context = None

        # User agents brasileiros reais
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

    async def _init_browser(self):
        """Inicializa navegador com configurações anti-detecção"""
        if self.browser:
            return

        playwright = await async_playwright().start()

        # Escolher user agent aleatório
        user_agent = random.choice(self.user_agents)

        # Iniciar navegador com opções anti-detecção
        self.browser = await playwright.chromium.launch(
            headless=True,  # True para produção, False para debug
            args=[
                '--disable-blink-features=AutomationControlled',  # Remove flag de automação
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )

        # Criar contexto com configurações realistas
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
            geolocation={'latitude': -23.5505, 'longitude': -46.6333},  # São Paulo
            permissions=['geolocation'],
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )

        # Remover flag webdriver
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Adicionar plugins realistas
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Adicionar idiomas
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
        """)

    async def _comportamento_humano(self, page: Page):
        """Simula comportamento humano na página"""
        # Delay inicial (humano lê a página)
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # Scroll suave e aleatório
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(100, 500)
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            await asyncio.sleep(random.uniform(0.2, 0.5))

        # Movimentos de mouse aleatórios
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 1000)
            y = random.randint(100, 800)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

    async def buscar_carrefour(self, termo: str) -> List[Dict]:
        """Busca REAL no Carrefour"""
        produtos = []
        try:
            await self._init_browser()
            page = await self.context.new_page()

            print(f"   🛒 Carrefour - Acessando...")

            # URL de busca do Carrefour
            url = f"https://www.carrefour.com.br/busca?q={termo.replace(' ', '%20')}"

            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            # Comportamento humano
            await self._comportamento_humano(page)

            # Aguardar produtos carregarem
            await page.wait_for_selector('[data-testid="product-card"]', timeout=10000)

            # Extrair produtos
            items = await page.locator('[data-testid="product-card"]').all()

            print(f"   📦 Carrefour - Encontrados {len(items)} items")

            for item in items[:15]:
                try:
                    # Nome
                    nome_elem = item.locator('[data-testid="product-name"]')
                    if await nome_elem.count() == 0:
                        nome_elem = item.locator('h3, h2, [class*="name"]')
                    nome = await nome_elem.first.inner_text()

                    # Preço
                    preco_elem = item.locator('[data-testid="price"], [class*="price"]')
                    preco_text = await preco_elem.first.inner_text()
                    preco = self._limpar_preco(preco_text)

                    if preco == 0:
                        continue

                    # URL
                    link = await item.locator('a').first.get_attribute('href')
                    url_produto = f"https://www.carrefour.com.br{link}" if link.startswith('/') else link

                    # Promoção
                    em_promocao = await item.locator('[class*="discount"], [class*="promo"]').count() > 0

                    produtos.append({
                        'nome': nome.strip(),
                        'marca': None,
                        'preco': preco,
                        'preco_original': None,
                        'em_promocao': em_promocao,
                        'url': url_produto,
                        'supermercado': 'Carrefour',
                        'disponivel': True,
                        'fonte': 'scraper_humano_avancado'
                    })

                except Exception as e:
                    continue

            await page.close()
            print(f"   ✅ Carrefour - {len(produtos)} produtos extraídos")

        except Exception as e:
            print(f"   ❌ Carrefour - Erro: {e}")

        return produtos

    async def buscar_paodeacucar(self, termo: str) -> List[Dict]:
        """Busca REAL no Pão de Açúcar"""
        produtos = []
        try:
            await self._init_browser()
            page = await self.context.new_page()

            print(f"   🛒 Pão de Açúcar - Acessando...")

            url = f"https://www.paodeacucar.com/busca?q={termo.replace(' ', '%20')}"

            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self._comportamento_humano(page)

            # Aguardar produtos
            await page.wait_for_selector('[data-testid="product-card"], .product-card, [class*="productCard"]', timeout=10000)

            items = await page.locator('[data-testid="product-card"], .product-card, [class*="productCard"]').all()

            print(f"   📦 Pão de Açúcar - Encontrados {len(items)} items")

            for item in items[:15]:
                try:
                    # Nome
                    nome = await item.locator('[data-testid="product-name"], h3, h2, [class*="name"]').first.inner_text()

                    # Preço
                    preco_text = await item.locator('[data-testid="price"], [class*="price"]').first.inner_text()
                    preco = self._limpar_preco(preco_text)

                    if preco == 0:
                        continue

                    # URL
                    link = await item.locator('a').first.get_attribute('href')
                    url_produto = f"https://www.paodeacucar.com{link}" if link.startswith('/') else link

                    # Promoção
                    em_promocao = await item.locator('[class*="discount"], [class*="sale"]').count() > 0

                    produtos.append({
                        'nome': nome.strip(),
                        'marca': None,
                        'preco': preco,
                        'em_promocao': em_promocao,
                        'url': url_produto,
                        'supermercado': 'Pão de Açúcar',
                        'disponivel': True,
                        'fonte': 'scraper_humano_avancado'
                    })

                except Exception:
                    continue

            await page.close()
            print(f"   ✅ Pão de Açúcar - {len(produtos)} produtos extraídos")

        except Exception as e:
            print(f"   ❌ Pão de Açúcar - Erro: {e}")

        return produtos

    async def buscar_extra(self, termo: str) -> List[Dict]:
        """Busca REAL no Extra"""
        produtos = []
        try:
            await self._init_browser()
            page = await self.context.new_page()

            print(f"   🛒 Extra - Acessando...")

            url = f"https://www.clubeextra.com.br/busca?q={termo.replace(' ', '%20')}"

            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await self._comportamento_humano(page)

            await page.wait_for_selector('[data-testid="product-card"], .product-card', timeout=10000)

            items = await page.locator('[data-testid="product-card"], .product-card').all()

            print(f"   📦 Extra - Encontrados {len(items)} items")

            for item in items[:15]:
                try:
                    nome = await item.locator('[data-testid="product-name"], h3, h2').first.inner_text()
                    preco_text = await item.locator('[data-testid="price"], [class*="price"]').first.inner_text()
                    preco = self._limpar_preco(preco_text)

                    if preco == 0:
                        continue

                    link = await item.locator('a').first.get_attribute('href')
                    url_produto = f"https://www.clubeextra.com.br{link}" if link.startswith('/') else link

                    produtos.append({
                        'nome': nome.strip(),
                        'preco': preco,
                        'url': url_produto,
                        'supermercado': 'Extra',
                        'disponivel': True,
                        'fonte': 'scraper_humano_avancado'
                    })

                except Exception:
                    continue

            await page.close()
            print(f"   ✅ Extra - {len(produtos)} produtos extraídos")

        except Exception as e:
            print(f"   ❌ Extra - Erro: {e}")

        return produtos

    async def buscar_todos(self, termo: str, supermercados: List[str] = None) -> List[Dict]:
        """
        Busca em múltiplos supermercados

        Args:
            termo: Termo de busca
            supermercados: Lista de supermercados ['carrefour', 'pao_acucar', 'extra']
                          Se None, busca em todos
        """
        if supermercados is None:
            supermercados = ['carrefour', 'pao_acucar', 'extra']

        todos_produtos = []

        print(f"\n🤖 SCRAPER HUMANO AVANÇADO - '{termo}'")
        print(f"{'='*70}")

        # Buscar em cada supermercado
        if 'carrefour' in supermercados:
            produtos = await self.buscar_carrefour(termo)
            todos_produtos.extend(produtos)
            await asyncio.sleep(random.uniform(1, 2))  # Delay entre sites

        if 'pao_acucar' in supermercados:
            produtos = await self.buscar_paodeacucar(termo)
            todos_produtos.extend(produtos)
            await asyncio.sleep(random.uniform(1, 2))

        if 'extra' in supermercados:
            produtos = await self.buscar_extra(termo)
            todos_produtos.extend(produtos)

        # Fechar navegador
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None

        print(f"{'='*70}")
        print(f"✅ Total: {len(todos_produtos)} produtos REAIS encontrados\n")

        return todos_produtos

    def _limpar_preco(self, preco_str: str) -> float:
        """Limpa string de preço brasileiro"""
        try:
            # Remove tudo exceto números, vírgula e ponto
            preco_str = re.sub(r'[^\d,.]', '', preco_str)

            # Se tem vírgula e ponto, remove ponto (separador de milhares)
            if ',' in preco_str and '.' in preco_str:
                preco_str = preco_str.replace('.', '')

            # Trocar vírgula por ponto (padrão brasileiro)
            preco_str = preco_str.replace(',', '.')

            return float(preco_str)
        except:
            return 0.0

    async def close(self):
        """Fecha navegador"""
        if self.browser:
            await self.browser.close()
            self.browser = None


# Função auxiliar síncrona
def buscar_produtos_supermercados(termo: str, supermercados: List[str] = None) -> List[Dict]:
    """
    Wrapper síncrono para buscar produtos

    Uso:
        produtos = buscar_produtos_supermercados('arroz', ['carrefour', 'pao_acucar'])
    """
    scraper = ScraperHumanoAvancado()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(scraper.buscar_todos(termo, supermercados))
    finally:
        loop.run_until_complete(scraper.close())


# Instância global
scraper_humano_avancado = ScraperHumanoAvancado()
