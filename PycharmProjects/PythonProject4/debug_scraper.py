"""
Debug script para ver estrutura HTML real do Mercado Livre
"""
import asyncio
from playwright.async_api import async_playwright


async def debug_mercadolivre():
    """Ver estrutura real da página"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='pt-BR',
        )

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = await context.new_page()

        url = "https://lista.mercadolivre.com.br/mouse-gamer"
        print(f"🔍 Acessando: {url}\n")

        await page.goto(url, wait_until='domcontentloaded', timeout=30000)

        # Esperar produtos
        try:
            await page.wait_for_selector('.ui-search-layout__item', timeout=10000)
            print("✅ Produtos carregaram\n")
        except:
            print("❌ Timeout aguardando produtos\n")
            await browser.close()
            return

        # Scroll
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
        await asyncio.sleep(2)

        # Pegar primeiro item
        items = await page.locator('.ui-search-layout__item').all()
        print(f"📊 Total de itens encontrados: {len(items)}\n")

        if len(items) > 0:
            print("🔎 Analisando PRIMEIRO item:\n")
            first_item = items[0]

            # Tentar diferentes seletores para nome
            nome_selectors = [
                'h2.ui-search-item__title',
                'h2',
                '.ui-search-item__title',
                '[class*="title"]'
            ]

            print("📝 Testando seletores de NOME:")
            for selector in nome_selectors:
                try:
                    elem = first_item.locator(selector)
                    count = await elem.count()
                    if count > 0:
                        text = await elem.first.inner_text()
                        print(f"  ✅ '{selector}': {count} elementos")
                        print(f"     Texto: {text[:80]}")
                    else:
                        print(f"  ❌ '{selector}': 0 elementos")
                except Exception as e:
                    print(f"  ❌ '{selector}': Erro - {e}")

            print("\n💰 Testando seletores de PREÇO:")
            preco_selectors = [
                '.andes-money-amount__fraction',
                '[class*="price"]',
                '[class*="amount"]',
                'span.andes-money-amount'
            ]

            for selector in preco_selectors:
                try:
                    elem = first_item.locator(selector)
                    count = await elem.count()
                    if count > 0:
                        text = await elem.first.inner_text()
                        print(f"  ✅ '{selector}': {count} elementos")
                        print(f"     Texto: {text}")
                    else:
                        print(f"  ❌ '{selector}': 0 elementos")
                except Exception as e:
                    print(f"  ❌ '{selector}': Erro - {e}")

            print("\n🔗 Testando seletores de LINK:")
            link_selectors = [
                'a',
                'a[href]',
                '.ui-search-link'
            ]

            for selector in link_selectors:
                try:
                    elem = first_item.locator(selector)
                    count = await elem.count()
                    if count > 0:
                        href = await elem.first.get_attribute('href')
                        print(f"  ✅ '{selector}': {count} elementos")
                        print(f"     URL: {href[:80] if href else 'None'}...")
                    else:
                        print(f"  ❌ '{selector}': 0 elementos")
                except Exception as e:
                    print(f"  ❌ '{selector}': Erro - {e}")

            # HTML completo do item (primeiros 500 caracteres)
            print("\n📄 HTML do primeiro item (primeiros 800 caracteres):")
            html = await first_item.inner_html()
            print(html[:800])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_mercadolivre())
