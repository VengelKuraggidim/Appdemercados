#!/usr/bin/env python3
"""
Teste dos scrapers com Selenium para supermercados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.carrefour_selenium import CarrefourSeleniumScraper
from app.scrapers.pao_acucar_selenium import PaoAcucarSeleniumScraper

def testar_scraper(scraper, nome, termo="arroz"):
    print(f"\n{'='*70}")
    print(f"🔍 Testando {nome} - Busca: {termo}")
    print('='*70)

    try:
        resultados = scraper.search(termo)

        if resultados:
            print(f"\n✅ {nome}: {len(resultados)} produtos encontrados\n")
            for i, produto in enumerate(resultados[:5], 1):
                print(f"{i}. {produto['nome'][:65]}")
                print(f"   💰 R$ {produto['preco']:.2f}")
                print(f"   {'🔥' if produto['em_promocao'] else '  '} Promoção: {'Sim' if produto['em_promocao'] else 'Não'}")
                if produto.get('url'):
                    print(f"   🔗 {produto['url'][:70]}...")
                print()
        else:
            print(f"\n⚠️  {nome}: Nenhum produto encontrado\n")

    except Exception as e:
        print(f"\n❌ {nome}: Erro - {str(e)}\n")

    finally:
        scraper.close()

if __name__ == "__main__":
    print("\n🛒 TESTE DE SCRAPERS COM SELENIUM")
    print("Este teste pode levar alguns minutos...")
    print("Baixando ChromeDriver se necessário...\n")

    # Testar Carrefour
    print("\n📍 1/2 - Carrefour")
    carrefour = CarrefourSeleniumScraper()
    testar_scraper(carrefour, "Carrefour", "arroz")

    # Testar Pão de Açúcar
    print("\n📍 2/2 - Pão de Açúcar")
    pao_acucar = PaoAcucarSeleniumScraper()
    testar_scraper(pao_acucar, "Pão de Açúcar", "feijão")

    print(f"\n{'='*70}")
    print("✅ Testes concluídos!")
    print('='*70 + "\n")
