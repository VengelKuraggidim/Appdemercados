#!/usr/bin/env python3
"""
Teste do scraper híbrido
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.scraper_hibrido import ScraperHibrido

def main():
    print("\n🛒 TESTE - Scraper Híbrido (Múltiplas Fontes)")
    print("="*70)

    scraper = ScraperHibrido()

    # Testar com alguns produtos
    termos = ["arroz tio joao", "feijao camil"]

    for termo in termos:
        resultados = scraper.search(termo)

        if resultados:
            print(f"\n✅ Resultados para '{termo}':\n")
            for i, produto in enumerate(resultados[:5], 1):
                print(f"{i}. {produto['nome'][:60]}")
                print(f"   💰 R$ {produto['preco']:.2f}")
                print(f"   🏪 {produto['supermercado']}")
                print()
        else:
            print(f"\n⚠️  Nenhum resultado para '{termo}'\n")

        print("-"*70)

    print("\n✅ Teste concluído!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
