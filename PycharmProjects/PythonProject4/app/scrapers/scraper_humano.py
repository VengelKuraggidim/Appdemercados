"""
Scraper que se comporta como um humano de verdade
Usa Selenium com técnicas avançadas anti-detecção
"""
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time
import random
import re


class ScraperHumano:
    """
    Scraper que imita comportamento humano para evitar detecção
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.wait_time = (2, 5)  # Tempos de espera aleatórios (min, max)

    def _init_driver(self):
        """Inicializa driver com técnicas anti-detecção"""
        if self.driver:
            return

        try:
            # Usar undetected-chromedriver que evita detecção automaticamente
            options = uc.ChromeOptions()

            if self.headless:
                options.add_argument('--headless=new')  # Nova forma de headless (menos detectável)

            # Configurações essenciais para ambientes Linux sem GUI
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-extensions')
            options.add_argument('--window-size=1920,1080')

            # User agent realista
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)

            # Remover propriedades que indicam automação
            try:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['pt-BR', 'pt', 'en-US', 'en']
                        });
                    '''
                })
            except:
                pass  # CDP pode não estar disponível

            print("   ✓ Driver anti-detecção inicializado")

        except Exception as e:
            print(f"   ⚠️  Erro ao inicializar undetected-chromedriver, usando chromedriver padrão: {e}")
            # Fallback para chromedriver normal com configurações para Linux
            options = Options()

            if self.headless:
                options.add_argument('--headless=new')

            # Configurações críticas para Linux
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Preferências
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
            }
            options.add_experimental_option("prefs", prefs)

            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

                # Tentar remover webdriver flag
                try:
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except:
                    pass

            except Exception as e2:
                print(f"   ❌ Erro ao inicializar ChromeDriver: {e2}")
                raise

    def _esperar_humano(self, min_time: float = None, max_time: float = None):
        """Espera um tempo aleatório imitando humano"""
        min_t = min_time if min_time else self.wait_time[0]
        max_t = max_time if max_time else self.wait_time[1]
        time.sleep(random.uniform(min_t, max_t))

    def _scroll_aleatorio(self):
        """Faz scroll aleatório na página (comportamento humano)"""
        try:
            # Scroll até o meio da página
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            self._esperar_humano(0.5, 1.5)

            # Scroll até o fim
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._esperar_humano(0.5, 1.5)

            # Volta um pouco
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
            self._esperar_humano(0.3, 0.8)
        except:
            pass

    def _mover_mouse_aleatorio(self):
        """Move o mouse aleatoriamente (comportamento humano)"""
        try:
            action = ActionChains(self.driver)
            # Mover para posição aleatória
            x_offset = random.randint(100, 800)
            y_offset = random.randint(100, 600)
            action.move_by_offset(x_offset, y_offset).perform()
            self._esperar_humano(0.1, 0.3)
        except:
            pass

    def _clean_price(self, price_str: str) -> float:
        """Limpa e converte string de preço para float"""
        try:
            # Remover tudo exceto dígitos, vírgula e ponto
            price_str = re.sub(r'[^\d,.]', '', price_str)

            # Se tem vírgula e ponto, remover ponto (separador de milhar)
            if ',' in price_str and '.' in price_str:
                price_str = price_str.replace('.', '')

            # Converter vírgula para ponto
            price_str = price_str.replace(',', '.')

            return float(price_str)
        except:
            return 0.0

    def buscar_carrefour(self, termo: str) -> List[Dict]:
        """Busca produtos no Carrefour com comportamento humano"""
        produtos = []

        try:
            self._init_driver()

            url = f"https://mercado.carrefour.com.br/busca?q={termo}"
            print(f"   🔍 Acessando Carrefour: {termo}")

            self.driver.get(url)
            self._esperar_humano(3, 5)  # Esperar página carregar

            # Comportamento humano: scroll
            self._scroll_aleatorio()

            # Esperar produtos carregarem com vários seletores possíveis
            selectors_container = [
                "div[data-testid='product-card']",
                "div[class*='ProductCard']",
                "div[class*='product-card']",
                "article[class*='product']"
            ]

            product_cards = []
            for selector in selectors_container:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    product_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_cards:
                        print(f"   ✓ Encontrados {len(product_cards)} produtos")
                        break
                except TimeoutException:
                    continue

            if not product_cards:
                print("   ⚠️  Nenhum produto encontrado")
                return produtos

            # Processar cada produto
            for i, card in enumerate(product_cards[:15]):
                try:
                    # Scroll até o card (comportamento humano)
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
                    self._esperar_humano(0.2, 0.5)

                    # Extrair nome
                    nome = None
                    for tag in ['h2', 'h3', 'h4', 'span[class*="title"]', 'a[class*="title"]', 'p[class*="title"]']:
                        try:
                            elem = card.find_element(By.CSS_SELECTOR, tag)
                            texto = elem.text.strip()
                            if texto and len(texto) > 3:
                                nome = texto
                                break
                        except:
                            continue

                    if not nome:
                        continue

                    # Extrair preço
                    preco = 0.0
                    preco_original = None

                    price_selectors = [
                        'span[class*="price"]',
                        'div[class*="price"]',
                        'p[class*="price"]',
                        'span[data-testid*="price"]',
                        'div[data-testid*="price"]'
                    ]

                    for selector in price_selectors:
                        try:
                            price_elems = card.find_elements(By.CSS_SELECTOR, selector)
                            for elem in price_elems:
                                texto = elem.text.strip()
                                if texto and any(char.isdigit() for char in texto):
                                    preco_temp = self._clean_price(texto)
                                    if preco_temp > 0:
                                        if preco == 0:
                                            preco = preco_temp
                                        elif preco_temp > preco and preco_original is None:
                                            preco_original = preco_temp
                                        break
                            if preco > 0:
                                break
                        except:
                            continue

                    if preco == 0:
                        continue

                    # Extrair URL
                    url_produto = ""
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a[href]')
                        url_produto = link.get_attribute('href')
                    except:
                        pass

                    # Verificar promoção
                    em_promocao = preco_original is not None and preco_original > preco

                    produtos.append({
                        'nome': nome,
                        'marca': None,
                        'preco': preco,
                        'preco_original': preco_original,
                        'em_promocao': em_promocao,
                        'url': url_produto,
                        'supermercado': 'Carrefour',
                        'disponivel': True
                    })

                except Exception as e:
                    print(f"   ⚠️  Erro ao processar produto {i+1}: {e}")
                    continue

            print(f"   ✅ Carrefour: {len(produtos)} produtos extraídos")

        except Exception as e:
            print(f"   ❌ Erro ao buscar no Carrefour: {e}")

        return produtos

    def buscar_pao_acucar(self, termo: str) -> List[Dict]:
        """Busca produtos no Pão de Açúcar"""
        produtos = []

        try:
            self._init_driver()

            url = f"https://www.paodeacucar.com/busca?q={termo}"
            print(f"   🔍 Acessando Pão de Açúcar: {termo}")

            self.driver.get(url)
            self._esperar_humano(3, 5)

            self._scroll_aleatorio()

            selectors_container = [
                "div[class*='ProductCard']",
                "div[class*='product-card']",
                "article[class*='product']",
                "li[class*='product']"
            ]

            product_cards = []
            for selector in selectors_container:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    product_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_cards:
                        print(f"   ✓ Encontrados {len(product_cards)} produtos")
                        break
                except TimeoutException:
                    continue

            if not product_cards:
                print("   ⚠️  Nenhum produto encontrado")
                return produtos

            for i, card in enumerate(product_cards[:15]):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
                    self._esperar_humano(0.2, 0.5)

                    # Nome
                    nome = None
                    for tag in ['h2', 'h3', 'h4', 'a[class*="name"]', 'span[class*="name"]', 'p[class*="name"]']:
                        try:
                            elem = card.find_element(By.CSS_SELECTOR, tag)
                            texto = elem.text.strip()
                            if texto and len(texto) > 3:
                                nome = texto
                                break
                        except:
                            continue

                    if not nome:
                        continue

                    # Preço
                    preco = 0.0
                    preco_original = None

                    for selector in ['span[class*="price"]', 'div[class*="price"]', 'p[class*="price"]']:
                        try:
                            price_elems = card.find_elements(By.CSS_SELECTOR, selector)
                            for elem in price_elems:
                                texto = elem.text.strip()
                                if texto and any(char.isdigit() for char in texto):
                                    preco_temp = self._clean_price(texto)
                                    if preco_temp > 0:
                                        if preco == 0:
                                            preco = preco_temp
                                        elif preco_temp > preco:
                                            preco_original = preco_temp
                                        break
                            if preco > 0:
                                break
                        except:
                            continue

                    if preco == 0:
                        continue

                    # URL
                    url_produto = ""
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a[href]')
                        url_produto = link.get_attribute('href')
                    except:
                        pass

                    em_promocao = preco_original is not None and preco_original > preco

                    produtos.append({
                        'nome': nome,
                        'marca': None,
                        'preco': preco,
                        'preco_original': preco_original,
                        'em_promocao': em_promocao,
                        'url': url_produto,
                        'supermercado': 'Pão de Açúcar',
                        'disponivel': True
                    })

                except Exception as e:
                    print(f"   ⚠️  Erro ao processar produto {i+1}: {e}")
                    continue

            print(f"   ✅ Pão de Açúcar: {len(produtos)} produtos extraídos")

        except Exception as e:
            print(f"   ❌ Erro ao buscar no Pão de Açúcar: {e}")

        return produtos

    def buscar_extra(self, termo: str) -> List[Dict]:
        """Busca produtos no Extra"""
        produtos = []

        try:
            self._init_driver()

            url = f"https://www.extra.com.br/busca?q={termo}"
            print(f"   🔍 Acessando Extra: {termo}")

            self.driver.get(url)
            self._esperar_humano(3, 5)

            self._scroll_aleatorio()

            # Extra usa estrutura similar ao Pão de Açúcar (mesmo grupo)
            selectors_container = [
                "div[class*='ProductCard']",
                "div[class*='product-card']",
                "article[class*='product']"
            ]

            product_cards = []
            for selector in selectors_container:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    product_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_cards:
                        print(f"   ✓ Encontrados {len(product_cards)} produtos")
                        break
                except TimeoutException:
                    continue

            if not product_cards:
                print("   ⚠️  Nenhum produto encontrado")
                return produtos

            for i, card in enumerate(product_cards[:15]):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
                    self._esperar_humano(0.2, 0.5)

                    # Nome
                    nome = None
                    for tag in ['h2', 'h3', 'h4', 'a', 'span', 'p']:
                        try:
                            elem = card.find_element(By.CSS_SELECTOR, tag)
                            texto = elem.text.strip()
                            if texto and len(texto) > 3 and not any(char.isdigit() for char in texto[:5]):
                                nome = texto
                                break
                        except:
                            continue

                    if not nome:
                        continue

                    # Preço
                    preco = 0.0
                    for selector in ['span', 'div', 'p']:
                        try:
                            price_elems = card.find_elements(By.CSS_SELECTOR, selector)
                            for elem in price_elems:
                                texto = elem.text.strip()
                                if 'R$' in texto or any(char.isdigit() for char in texto):
                                    preco_temp = self._clean_price(texto)
                                    if preco_temp > 0:
                                        preco = preco_temp
                                        break
                            if preco > 0:
                                break
                        except:
                            continue

                    if preco == 0:
                        continue

                    url_produto = ""
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a[href]')
                        url_produto = link.get_attribute('href')
                    except:
                        pass

                    produtos.append({
                        'nome': nome,
                        'marca': None,
                        'preco': preco,
                        'em_promocao': False,
                        'url': url_produto,
                        'supermercado': 'Extra',
                        'disponivel': True
                    })

                except Exception as e:
                    continue

            print(f"   ✅ Extra: {len(produtos)} produtos extraídos")

        except Exception as e:
            print(f"   ❌ Erro ao buscar no Extra: {e}")

        return produtos

    def buscar_todos(self, termo: str, mercados: List[str] = None) -> List[Dict]:
        """
        Busca em todos os mercados ou apenas nos especificados
        """
        print(f"\n{'='*60}")
        print(f"🛒 BUSCANDO: '{termo}'")
        print(f"{'='*60}")

        mercados_disponiveis = {
            'carrefour': self.buscar_carrefour,
            'pao_acucar': self.buscar_pao_acucar,
            'extra': self.buscar_extra
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

                # Esperar entre mercados (comportamento humano)
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
        print(f"✅ TOTAL: {len(resultado)} produtos únicos encontrados")
        print(f"{'='*60}\n")

        return resultado

    def close(self):
        """Fecha o driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __del__(self):
        """Destrutor"""
        self.close()


# Instância global para reutilizar sessão
_scraper_instance = None

def get_scraper_humano(headless: bool = True) -> ScraperHumano:
    """Retorna instância global do scraper"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = ScraperHumano(headless=headless)
    return _scraper_instance
