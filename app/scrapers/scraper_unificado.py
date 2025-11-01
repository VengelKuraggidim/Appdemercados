"""
Sistema Unificado de Scraping Inteligente
Tenta múltiplas estratégias até conseguir resultados
"""
from typing import List, Dict, Optional
import time


class ScraperUnificado:
    """
    Sistema inteligente que tenta:
    1. APIs públicas (mais rápido e confiável)
    2. Playwright (moderno, menos detectável)
    3. Selenium anti-detecção (fallback)
    4. Requests simples (último recurso)
    """

    def __init__(self):
        self.scrapers = {}
        self.resultados_cache = {}

    def _get_scraper_apis(self):
        """Lazy load do scraper de APIs"""
        if 'apis' not in self.scrapers:
            try:
                from app.scrapers.scraper_apis import scraper_apis
                self.scrapers['apis'] = scraper_apis
                print("   ✓ Scraper de APIs carregado")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar scraper de APIs: {e}")
                self.scrapers['apis'] = None
        return self.scrapers['apis']

    def _get_scraper_playwright(self):
        """Lazy load do Playwright"""
        if 'playwright' not in self.scrapers:
            try:
                from app.scrapers.scraper_playwright import get_scraper_playwright
                self.scrapers['playwright'] = get_scraper_playwright(headless=True)
                print("   ✓ Playwright carregado")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar Playwright: {e}")
                self.scrapers['playwright'] = None
        return self.scrapers['playwright']

    def _get_scraper_selenium(self):
        """Lazy load do Selenium"""
        if 'selenium' not in self.scrapers:
            try:
                from app.scrapers.scraper_humano import get_scraper_humano
                self.scrapers['selenium'] = get_scraper_humano(headless=True)
                print("   ✓ Selenium anti-detecção carregado")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar Selenium: {e}")
                self.scrapers['selenium'] = None
        return self.scrapers['selenium']

    def _get_scraper_simples(self):
        """Lazy load do scraper simples"""
        if 'simples' not in self.scrapers:
            try:
                from app.scrapers.scraper_simples import scraper_simples
                self.scrapers['simples'] = scraper_simples
                print("   ✓ Scraper simples carregado")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar scraper simples: {e}")
                self.scrapers['simples'] = None
        return self.scrapers['simples']

    def buscar_inteligente(
        self,
        termo: str,
        minimo_produtos: int = 5,
        timeout_por_estrategia: int = 30
    ) -> List[Dict]:
        """
        Busca inteligente com múltiplas estratégias
        Para assim que conseguir produtos suficientes
        """
        print(f"\n{'='*70}")
        print(f"🧠 SCRAPER UNIFICADO INTELIGENTE: '{termo}'")
        print(f"{'='*70}")
        print(f"Objetivo: Mínimo {minimo_produtos} produtos\n")

        todos_produtos = []

        # Estratégia 1: APIs (Mais rápido e confiável)
        print("📡 Estratégia 1: APIs Públicas")
        print("-" * 70)
        try:
            scraper_apis = self._get_scraper_apis()
            if scraper_apis:
                start_time = time.time()
                produtos_api = scraper_apis.buscar_todos(termo)

                todos_produtos.extend(produtos_api)

                elapsed = time.time() - start_time
                print(f"   ⏱️  Tempo: {elapsed:.2f}s")
                print(f"   📊 Produtos encontrados: {len(produtos_api)}")

                if len(todos_produtos) >= minimo_produtos:
                    print(f"\n✅ Objetivo alcançado com APIs! ({len(todos_produtos)} produtos)")
                    return self._remover_duplicatas(todos_produtos)
        except Exception as e:
            print(f"   ❌ Erro na estratégia de APIs: {e}")

        print()

        # Estratégia 2: Playwright (Moderno e menos detectável)
        if len(todos_produtos) < minimo_produtos:
            print("🎭 Estratégia 2: Playwright (Navegador Moderno)")
            print("-" * 70)
            try:
                scraper_playwright = self._get_scraper_playwright()
                if scraper_playwright:
                    start_time = time.time()

                    # Tentar mercados específicos
                    mercados = ['mercadolivre', 'carrefour']
                    produtos_pw = scraper_playwright.buscar_todos(termo, mercados=mercados)

                    todos_produtos.extend(produtos_pw)

                    elapsed = time.time() - start_time
                    print(f"   ⏱️  Tempo: {elapsed:.2f}s")
                    print(f"   📊 Produtos encontrados: {len(produtos_pw)}")

                    if len(todos_produtos) >= minimo_produtos:
                        print(f"\n✅ Objetivo alcançado com Playwright! ({len(todos_produtos)} produtos)")
                        return self._remover_duplicatas(todos_produtos)
            except Exception as e:
                print(f"   ❌ Erro na estratégia Playwright: {e}")

            print()

        # Estratégia 3: Selenium Anti-Detecção (Fallback)
        if len(todos_produtos) < minimo_produtos:
            print("🤖 Estratégia 3: Selenium Anti-Detecção")
            print("-" * 70)
            try:
                scraper_selenium = self._get_scraper_selenium()
                if scraper_selenium:
                    start_time = time.time()

                    mercados = ['carrefour', 'pao_acucar']
                    produtos_sel = scraper_selenium.buscar_todos(termo, mercados=mercados)

                    todos_produtos.extend(produtos_sel)

                    elapsed = time.time() - start_time
                    print(f"   ⏱️  Tempo: {elapsed:.2f}s")
                    print(f"   📊 Produtos encontrados: {len(produtos_sel)}")

                    if len(todos_produtos) >= minimo_produtos:
                        print(f"\n✅ Objetivo alcançado com Selenium! ({len(todos_produtos)} produtos)")
                        return self._remover_duplicatas(todos_produtos)
            except Exception as e:
                print(f"   ❌ Erro na estratégia Selenium: {e}")

            print()

        # Estratégia 4: Requests Simples (Último recurso)
        if len(todos_produtos) < minimo_produtos:
            print("📦 Estratégia 4: Requests Simples (Último Recurso)")
            print("-" * 70)
            try:
                scraper_simples = self._get_scraper_simples()
                if scraper_simples:
                    start_time = time.time()
                    produtos_simples = scraper_simples.buscar_todos(termo)

                    todos_produtos.extend(produtos_simples)

                    elapsed = time.time() - start_time
                    print(f"   ⏱️  Tempo: {elapsed:.2f}s")
                    print(f"   📊 Produtos encontrados: {len(produtos_simples)}")
            except Exception as e:
                print(f"   ❌ Erro na estratégia simples: {e}")

        # Resultado final
        resultado = self._remover_duplicatas(todos_produtos)

        print(f"\n{'='*70}")
        if len(resultado) >= minimo_produtos:
            print(f"✅ SUCESSO! {len(resultado)} produtos encontrados")
        elif len(resultado) > 0:
            print(f"⚠️  PARCIAL: {len(resultado)} produtos (mínimo: {minimo_produtos})")
        else:
            print(f"❌ FALHA: Nenhum produto encontrado")
        print(f"{'='*70}\n")

        return resultado

    def _remover_duplicatas(self, produtos: List[Dict]) -> List[Dict]:
        """Remove produtos duplicados"""
        produtos_unicos = {}
        for p in produtos:
            # Chave baseada em nome + supermercado + preço
            key = f"{p['nome'][:30].lower()}_{p['supermercado']}_{p.get('preco', 0):.2f}"
            if key not in produtos_unicos:
                produtos_unicos[key] = p

        return list(produtos_unicos.values())

    def buscar_rapido(self, termo: str) -> List[Dict]:
        """Busca rápida - apenas APIs"""
        print(f"\n⚡ BUSCA RÁPIDA (apenas APIs): '{termo}'")

        scraper_apis = self._get_scraper_apis()
        if scraper_apis:
            return scraper_apis.buscar_todos(termo)

        return []

    def buscar_completo(self, termo: str) -> List[Dict]:
        """Busca completa - todas as estratégias"""
        return self.buscar_inteligente(termo, minimo_produtos=10)

    def close_all(self):
        """Fecha todos os scrapers"""
        print("\n🔧 Fechando scrapers...")

        if 'playwright' in self.scrapers and self.scrapers['playwright']:
            try:
                self.scrapers['playwright'].close()
                print("   ✓ Playwright fechado")
            except:
                pass

        if 'selenium' in self.scrapers and self.scrapers['selenium']:
            try:
                self.scrapers['selenium'].close()
                print("   ✓ Selenium fechado")
            except:
                pass

        print("✅ Scrapers fechados\n")


# Instância global
scraper_unificado = ScraperUnificado()
