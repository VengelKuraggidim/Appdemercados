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


class CarrefourSeleniumScraper:
    """Scraper para Carrefour usando Selenium"""

    def __init__(self):
        self.base_url = "https://mercado.carrefour.com.br"
        self.driver = None

    def _init_driver(self):
        """Inicializa o driver do Chrome"""
        if self.driver:
            return

        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Executar sem interface gráfica
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def get_supermercado_name(self) -> str:
        return "Carrefour"

    def _clean_price(self, price_str: str) -> float:
        """Limpa e converte string de preço para float"""
        try:
            # Remover R$, espaços e converter vírgula para ponto
            price_str = re.sub(r'[^\d,]', '', price_str)
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except:
            return 0.0

    def search(self, termo: str) -> List[Dict]:
        """Busca produtos no Carrefour"""
        try:
            self._init_driver()

            # URL de busca
            search_url = f"{self.base_url}/busca?q={termo}"
            print(f"   Acessando: {search_url}")

            self.driver.get(search_url)

            # Aguardar carregamento da página
            time.sleep(3)

            # Esperar produtos carregarem
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='product-card'], article, div.product"))
                )
            except:
                print("   Nenhum produto encontrado ou timeout")
                return []

            produtos = []

            # Diferentes seletores possíveis para cards de produtos
            selectors = [
                "div[data-testid='product-card']",
                "article[class*='product']",
                "div[class*='product-card']",
                "div[class*='ProductCard']"
            ]

            product_cards = []
            for selector in selectors:
                product_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if product_cards:
                    print(f"   Encontrados {len(product_cards)} produtos com seletor: {selector}")
                    break

            for i, card in enumerate(product_cards[:15]):  # Limitar a 15 produtos
                try:
                    # Extrair nome do produto
                    nome = None
                    for tag in ['h2', 'h3', 'h4', 'span[class*="title"]', 'a[class*="title"]']:
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
                        'p[class*="price"]',
                        'span[data-testid*="price"]'
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

                    # Verificar se está em promoção
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
            print(f"   Erro ao buscar no Carrefour: {e}")
            return []

    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        """Destrutor para garantir que o driver seja fechado"""
        self.close()
