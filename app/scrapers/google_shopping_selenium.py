"""
Google Shopping Scraper usando Selenium/Playwright
Este método é mais robusto mas mais lento
"""

from typing import List, Dict
from urllib.parse import quote
import re
import time


class GoogleShoppingSeleniumScraper:
    """Scraper for Google Shopping using Selenium (real browser)"""

    def __init__(self):
        self.base_url = "https://www.google.com.br"

    def search(self, termo: str) -> List[Dict]:
        """
        Search using Selenium for better success rate
        Note: Requires selenium and chromedriver installed
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            print("❌ Selenium não instalado. Instale com: pip install selenium")
            return []

        termo_encoded = quote(termo)
        search_url = f"{self.base_url}/search?q={termo_encoded}+preço+comprar&hl=pt-BR"

        print(f"🔍 Buscando com Selenium: {termo}")

        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        produtos = []

        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(search_url)

            # Wait for results to load
            time.sleep(3)

            # Get page source
            page_source = driver.page_source

            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'lxml')

            # Find all search result divs
            results = soup.find_all('div', class_='g')

            print(f"   Encontrados {len(results)} resultados")

            for result in results[:20]:
                try:
                    # Get title
                    title_elem = result.find('h3')
                    if not title_elem:
                        continue

                    nome = title_elem.text.strip()

                    # Get text content
                    text = result.get_text()

                    # Find price pattern
                    price_match = re.search(r'R\$\s*(\d+[.,]\d{2})', text)
                    if not price_match:
                        continue

                    preco_str = price_match.group(1).replace('.', '').replace(',', '.')
                    preco = float(preco_str)

                    # Get URL
                    link = result.find('a', href=True)
                    url = link['href'] if link else ""
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]

                    # Identify store
                    supermercado = self._identificar_supermercado(url, text)

                    # Check promotion
                    em_promocao = bool(re.search(r'(promoção|oferta|desconto)', text, re.IGNORECASE))

                    produtos.append({
                        'nome': nome,
                        'marca': None,
                        'preco': preco,
                        'em_promocao': em_promocao,
                        'url': url,
                        'supermercado': supermercado,
                        'disponivel': True
                    })

                    print(f"   ✓ {nome[:50]}... - R$ {preco:.2f}")

                except Exception as e:
                    continue

            driver.quit()
            print(f"   Total: {len(produtos)} produtos")

        except Exception as e:
            print(f"   ✗ Erro: {e}")

        return produtos

    def _identificar_supermercado(self, url: str, texto: str) -> str:
        """Identify supermarket from URL or text"""
        url_lower = url.lower()
        texto_lower = texto.lower()

        mercados = {
            'carrefour': 'carrefour',
            'paodeacucar': 'pao_acucar',
            'extra': 'extra',
            'mercadolivre': 'mercado_livre',
            'atacadao': 'atacadao',
            'americanas': 'americanas',
            'magazine': 'magazine_luiza',
        }

        for keyword, name in mercados.items():
            if keyword in url_lower or keyword.replace('_', ' ') in texto_lower:
                return name

        return 'online'
