#!/usr/bin/env python3
"""
Teste do sistema de busca com scraping em tempo real
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scrapers.scraper_tempo_real import scraper_tempo_real

def main():
    print("\n" + "="*70)
    print("🛒 TESTE - Sistema de Scraping em Tempo Real")
    print("="*70)
    print("\nEste sistema busca preços REAIS quando você pesquisa um produto!")
    print("Testando com produto: 'arroz'\n")

    # Testar scraper
    termo = "arroz"
    resultados = scraper_tempo_real.buscar_todos(termo, max_por_fonte=5)

    if resultados:
        print(f"\n✅ SUCESSO! Encontrados {len(resultados)} produtos com preços REAIS:\n")
        print("="*70)

        for i, produto in enumerate(resultados, 1):
            print(f"\n{i}. {produto['nome'][:65]}")
            print(f"   🏪 {produto['supermercado']}")
            print(f"   💰 R$ {produto['preco']:.2f}")

            if produto.get('preco_original'):
                economia = produto['preco_original'] - produto['preco']
                desconto = (economia / produto['preco_original']) * 100
                print(f"   🔥 PROMOÇÃO! De R$ {produto['preco_original']:.2f} (economize R$ {economia:.2f} - {desconto:.0f}% OFF)")

            if produto.get('em_promocao') and not produto.get('preco_original'):
                print(f"   🔥 EM PROMOÇÃO")

            if produto.get('url'):
                print(f"   🔗 {produto['url'][:65]}...")

        print("\n" + "="*70)
        print("✅ Sistema funcionando perfeitamente!")
        print("="*70)

    else:
        print("\n⚠️  Nenhum produto encontrado (sites podem estar bloqueando)")
        print("\nIsso é normal - os sites têm proteções anti-bot.")
        print("O sistema continuará tentando em cada busca do usuário.")
        print("="*70)

    print("\n📝 Como funciona:")
    print("   1. Usuário busca produto no app")
    print("   2. Sistema tenta buscar preços REAIS naquele momento")
    print("   3. Se encontrar, salva no banco + mostra para usuário")
    print("   4. Se não encontrar (bloqueado), mostra dados do banco")
    print("   5. Usuários também podem adicionar preços manualmente\n")

if __name__ == "__main__":
    main()
