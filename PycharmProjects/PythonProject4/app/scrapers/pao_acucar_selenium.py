from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


class PaoAcucarSeleniumScraper:
    """Scraper para Pão de Açúcar usando Selenium"""

    def __init__(self):
        self.base_url = "https://www.paodeacucar.com"
        self.driver = None

    def _init_driver(self):
        """Inicializa o driver do Chrome"""
        if self.driver:
            return

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def get_supermercado_name(self) -> str:
        return "Pão de Açúcar"

    def _clean_price(self, price_str: str) -> float:
        """Limpa e converte string de preço para float"""
        try:
            price_str = re.sub(r'[^\d,]', '', price_str)
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0

    def search(self, termo: str) -> List[Dict]:
        """Busca produtos no Pão de Açúcar"""
        try:
            self._init_driver()

            search_url = f"{self.base_url}/busca?q={termo}"
            print(f"   Acessando: {search_url}")

            self.driver.get(search_url)
            time.sleep(3)

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='product'], article, li[class*='product']"))
                )
            except:
                print("   Nenhum produto encontrado ou timeout")
                return []

            produtos = []

            selectors = [
                "div[class*='ProductCard']",
                "div[class*='product-card']",
                "article[class*='product']",
                "li[class*='product-item']"
            ]

            product_cards = []
            for selector in selectors:
                product_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if product_cards:
                    print(f"   Encontrados {len(product_cards)} produtos com seletor: {selector}")
                    break

            for i, card in enumerate(product_cards[:15]):
                try:
                    # Extrair nome
                    nome = None
                    for tag in ['h2', 'h3', 'h4', 'a[class*="name"]', 'span[class*="name"]']:
                        try:
                            nome_elem = card.find_element(By.CSS_SELECTOR, tag)
                            nome = nome_elem.text.strip()
                            if nome and len(nome) > 3:
                                break
                        except:
                            continue

                    if not nome:
                        continue

                    # Extrair preço
                    preco = 0.0
                    for selector in [
                        'span[class*="price"]',
                        'div[class*="price"]',
                        'p[class*="price"]'
                    ]:
                        try:
                            preco_elem = card.find_element(By.CSS_SELECTOR, selector)
                            preco_text = preco_elem.text.strip()
                            preco = self._clean_price(preco_text)
                            if preco > 0:
                                break
                        except:
                            continue

                    if preco == 0:
                        continue

                    # Extrair URL
                    url = ""
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                        url = link_elem.get_attribute('href')
                    except:
                        pass

                    # Verificar promoção
                    em_promocao = False
                    try:
                        promo_keywords = ['promo', 'desconto', 'oferta', 'sale']
                        card_html = card.get_attribute('outerHTML').lower()
                        em_promocao = any(keyword in card_html for keyword in promo_keywords)
                    except:
                        pass

                    produtos.append({
                        'nome': nome,
                        'marca': None,
                        'preco': preco,
                        'em_promocao': em_promocao,
                        'url': url,
                        'supermercado': self.get_supermercado_name(),
                        'disponivel': True
                    })

                except Exception as e:
                    print(f"   Erro ao processar produto {i+1}: {e}")
                    continue

            print(f"   ✓ Extraídos {len(produtos)} produtos válidos")
            return produtos

        except Exception as e:
            print(f"   Erro ao buscar no Pão de Açúcar: {e}")
            return []

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close()
