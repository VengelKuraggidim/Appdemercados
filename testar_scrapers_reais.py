#!/usr/bin/env python3
"""
Script para testar scrapers reais de supermercados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.carrefour import CarrefourScraper
from app.scrapers.pao_acucar import PaoAcucarScraper
from app.scrapers.extra import ExtraScraper
from app.scrapers.mercado_livre import MercadoLivreScraper

def testar_scraper(scraper, nome):
    print(f"\n{'='*60}")
    print(f"🔍 Testando {nome}...")
    print('='*60)

    try:
        # Testar busca por arroz
        resultados = scraper.search("arroz")

        if resultados:
            print(f"✅ {nome}: {len(resultados)} produtos encontrados")
            print(f"\nPrimeiros 3 produtos:")
            for i, produto in enumerate(resultados[:3], 1):
                print(f"\n{i}. {produto.get('nome', 'N/A')}")
                print(f"   Marca: {produto.get('marca', 'N/A')}")
                print(f"   Preço: R$ {produto.get('preco', 'N/A')}")
                print(f"   Promoção: {'Sim' if produto.get('em_promocao') else 'Não'}")
                print(f"   URL: {produto.get('url', 'N/A')[:80]}...")
        else:
            print(f"⚠️  {nome}: Nenhum produto encontrado")

    except Exception as e:
        print(f"❌ {nome}: Erro - {str(e)}")

if __name__ == "__main__":
    print("\n🛒 TESTE DE SCRAPERS DE SUPERMERCADOS")
    print("Buscando por: arroz\n")

    scrapers = [
        (CarrefourScraper(), "Carrefour"),
        (PaoAcucarScraper(), "Pão de Açúcar"),
        (ExtraScraper(), "Extra"),
        (MercadoLivreScraper(), "Mercado Livre")
    ]

    for scraper, nome in scrapers:
        testar_scraper(scraper, nome)

    print(f"\n{'='*60}")
    print("✅ Testes concluídos!")
    print('='*60 + "\n")
