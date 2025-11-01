"""
Scraper REAL usando Playwright
Busca produtos REAIS da web sob demanda
"""
from typing import List, Dict, Optional
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import re
import time


class ScraperRealPlaywright:
    """
    Scraper que busca produtos REAIS sob demanda
    Usa Playwright para simular navegação humana real
    """

    def __init__(self):
        self.browser = None
        self.context = None
        self.playwright = None

    async def _init_browser(self):
        """Inicializa browser com configurações anti-detecção"""
        if self.browser:
            return

        self.playwright = await async_playwright().start()

        # Usar Chromium com configurações que funcionam
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Headless para produção
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )

        # Contexto com headers realistas
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )

        # Script anti-detecção
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        """)

        print("   ✓ Browser Playwright inicializado")

    def _clean_price(self, text: str) -> float:
        """Extrai preço de texto"""
        try:
            # Remover espaços e símbolos
            text = text.strip().replace('R$', '').replace(' ', '').replace('\n', '')

            # Se já tem ponto decimal
            if '.' in text and ',' not in text:
                return float(text)

            # Se tem vírgula como decimal
            if ',' in text:
                text = text.replace('.', '').replace(',', '.')
                return float(text)

            # Só números (assumir que é inteiro)
            if text.isdigit():
                return float(text)

            # Tentar regex
            match = re.search(r'(\d+(?:[.,]\d{2})?)', text)
            if match:
                price_str = match.group(1).replace(',', '.')
                return float(price_str)

            return 0.0
        except Exception as e:
            return 0.0

    async def buscar_mercadolivre_real(self, termo: str) -> List[Dict]:
        """Busca REAL no Mercado Livre"""
        produtos = []

        try:
            await self._init_browser()
            page = await self.context.new_page()

            url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
            print(f"   🔍 Acessando Mercado Livre: {url}")

            # Navegar
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)

            # Esperar produtos carregarem
            try:
                await page.wait_for_selector('.ui-search-layout__item', timeout=10000)
            except:
                print("   ⚠️  Timeout aguardando produtos")
                await page.close()
                return []

            # Scroll para carregar mais produtos
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
            await asyncio.sleep(2)

            # Pegar produtos
            items = await page.locator('.ui-search-layout__item').all()
            print(f"   ✓ Encontrados {len(items)} itens")

            for item in items[:15]:
                try:
                    # Nome - usar seletor genérico que funciona
                    nome_elem = item.locator('[class*="title"]')
                    if await nome_elem.count() == 0:
                        continue

                    nome = await nome_elem.first.inner_text()
                    nome = nome.strip()

                    if not nome or len(nome) < 3:
                        continue

                    # Preço - pegar fração completa
                    preco_fracao = item.locator('.andes-money-amount__fraction')
                    preco_centavos = item.locator('.andes-money-amount__cents')

                    if await preco_fracao.count() == 0:
                        continue

                    # Pegar primeira fração (preço atual)
                    preco_text = await preco_fracao.first.inner_text()

                    # Tentar pegar centavos se existir
                    if await preco_centavos.count() > 0:
                        centavos = await preco_centavos.first.inner_text()
                        preco_text = f"{preco_text}.{centavos}"
                    else:
                        preco_text = f"{preco_text}.00"

                    preco = self._clean_price(preco_text)

                    if preco == 0:
                        continue

                    # URL
                    link_elem = item.locator('a')
                    if await link_elem.count() == 0:
                        url_produto = ''
                    else:
                        url_produto = await link_elem.first.get_attribute('href')
                        if not url_produto:
                            url_produto = ''

                    # Desconto - verificar se tem "% OFF"
                    item_html = await item.inner_text()
                    em_promocao = '% OFF' in item_html or 'OFF' in item_html

                    produtos.append({
                        'nome': nome.strip(),
                        'marca': None,
                        'preco': preco,
                        'em_promocao': em_promocao,
                        'url': url_produto,
                        'supermercado': 'Mercado Livre',
                        'disponivel': True,
                        'fonte': 'scraping_real'
                    })

                except Exception as e:
                    continue

            await page.close()
            print(f"   ✅ Mercado Livre: {len(produtos)} produtos REAIS")

        except Exception as e:
            print(f"   ❌ Erro Mercado Livre: {e}")

        return produtos

    async def buscar_google_shopping_real(self, termo: str) -> List[Dict]:
        """Busca REAL no Google Shopping"""
        produtos = []

        try:
            await self._init_browser()
            page = await self.context.new_page()

            url = f"https://www.google.com/search?q={termo}&tbm=shop&hl=pt-BR"
            print(f"   🔍 Acessando Google Shopping...")

            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)

            # Tentar diferentes seletores do Google Shopping
            selectors = [
                '.sh-dgr__content',
                '[data-sh-product]',
                '.sh-pr__product-results'
            ]

            items = []
            for selector in selectors:
                items = await page.locator(selector).all()
                if len(items) > 0:
                    print(f"   ✓ Encontrados {len(items)} itens")
                    break

            for item in items[:10]:
                try:
                    # Nome
                    nome_elem = item.locator('h3, h4')
                    if await nome_elem.count() == 0:
                        continue
                    nome = await nome_elem.first.inner_text()

                    # Preço
                    preco_elem = item.locator('[class*="price"], b')
                    if await preco_elem.count() == 0:
                        continue

                    preco_text = await preco_elem.first.inner_text()
                    preco = self._clean_price(preco_text)

                    if preco == 0:
                        continue

                    # Loja
                    loja_elem = item.locator('[class*="merchant"], [class*="store"]')
                    loja = 'Google Shopping'
                    if await loja_elem.count() > 0:
                        loja = await loja_elem.first.inner_text()

                    # URL
                    link_elem = item.locator('a').first
                    url_produto = await link_elem.get_attribute('href') if await link_elem.count() > 0 else ''

                    produtos.append({
                        'nome': nome.strip(),
                        'marca': None,
                        'preco': preco,
                        'em_promocao': False,
                        'url': url_produto,
                        'supermercado': loja.strip() if loja else 'Google Shopping',
                        'disponivel': True,
                        'fonte': 'scraping_real'
                    })

                except Exception:
                    continue

            await page.close()
            print(f"   ✅ Google Shopping: {len(produtos)} produtos REAIS")

        except Exception as e:
            print(f"   ❌ Erro Google Shopping: {e}")

        return produtos

    async def buscar_todos_async(self, termo: str) -> List[Dict]:
        """Busca em todas as fontes (async)"""
        print(f"\n{'='*60}")
        print(f"🌐 SCRAPING REAL: '{termo}'")
        print(f"{'='*60}")

        todos_produtos = []

        # Mercado Livre
        produtos_ml = await self.buscar_mercadolivre_real(termo)
        todos_produtos.extend(produtos_ml)

        # Google Shopping
        await asyncio.sleep(2)  # Delay entre fontes
        produtos_gs = await self.buscar_google_shopping_real(termo)
        todos_produtos.extend(produtos_gs)

        # Remover duplicatas
        produtos_unicos = {}
        for p in todos_produtos:
            key = f"{p['nome'][:40].lower()}_{p['preco']:.2f}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        resultado = list(produtos_unicos.values())

        print(f"\n{'='*60}")
        print(f"✅ TOTAL: {len(resultado)} produtos REAIS encontrados")
        print(f"{'='*60}\n")

        return resultado

    def buscar_todos(self, termo: str) -> List[Dict]:
        """Wrapper síncrono para busca async"""
        return asyncio.run(self.buscar_todos_async(termo))

    async def close(self):
        """Fecha browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def __del__(self):
        """Destrutor"""
        try:
            asyncio.run(self.close())
        except:
            pass


# Função helper para uso direto
def buscar_produtos_reais(termo: str) -> List[Dict]:
    """
    Busca produtos REAIS da web
    Uso: produtos = buscar_produtos_reais("arroz")
    """
    scraper = ScraperRealPlaywright()
    return scraper.buscar_todos(termo)
