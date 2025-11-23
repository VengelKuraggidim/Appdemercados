#!/usr/bin/env python3
"""
Teste do scraper do Mercado Livre com API oficial
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.mercado_livre import MercadoLivreScraper

def main():
    print("\n🛒 TESTE - Mercado Livre API")
    print("="*60)

    scraper = MercadoLivreScraper()

    # Testar com diferentes produtos
    produtos_teste = ["arroz", "feijão", "café", "açúcar"]

    for termo in produtos_teste:
        print(f"\n🔍 Buscando: {termo}")
        print("-"*60)

        resultados = scraper.search(termo)

        if resultados:
            print(f"✅ Encontrados {len(resultados)} produtos\n")
            for i, produto in enumerate(resultados[:5], 1):
                print(f"{i}. {produto['nome'][:60]}")
                print(f"   💰 R$ {produto['preco']:.2f}")
                if produto.get('preco_original'):
                    print(f"   🔥 De: R$ {produto['preco_original']:.2f}")
                print(f"   {'🔥' if produto['em_promocao'] else '  '} Promoção: {'Sim' if produto['em_promocao'] else 'Não'}")
                print()
        else:
            print("⚠️  Nenhum produto encontrado\n")

    print("="*60)
    print("✅ Teste concluído!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
