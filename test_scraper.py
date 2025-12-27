#!/usr/bin/env python3
"""
Script de teste para os scrapers
Use este script para testar se os scrapers estão funcionando
"""

from app.scrapers.scraper_manager import ScraperManager
import sys


def testar_scraper(termo_busca: str):
    print(f"\n🔍 Testando busca por: '{termo_busca}'")
    print("=" * 60)

    manager = ScraperManager()

    print("\nSupermercados disponíveis:")
    for market in manager.get_available_supermarkets():
        print(f"  • {market}")

    print(f"\n📦 Buscando produtos em todos os supermercados...")
    print("-" * 60)

    produtos = manager.search_all(termo_busca)

    if produtos:
        print(f"\n✅ Total de produtos encontrados: {len(produtos)}")
        print("\n📊 Resultados por supermercado:")

        # Group by supermarket
        por_mercado = {}
        for p in produtos:
            mercado = p['supermercado']
            if mercado not in por_mercado:
                por_mercado[mercado] = []
            por_mercado[mercado].append(p)

        for mercado, items in por_mercado.items():
            print(f"\n  {mercado.upper()}: {len(items)} produtos")
            # Show cheapest 3
            items_sorted = sorted(items, key=lambda x: x['preco'])[:3]
            for i, item in enumerate(items_sorted, 1):
                promo = "🔥" if item.get('em_promocao') else "  "
                print(f"    {i}. {promo} R$ {item['preco']:.2f} - {item['nome'][:50]}")

        # Show overall best price
        melhor = min(produtos, key=lambda x: x['preco'])
        print(f"\n💰 MELHOR PREÇO GERAL:")
        print(f"   R$ {melhor['preco']:.2f}")
        print(f"   {melhor['nome']}")
        print(f"   {melhor['supermercado'].upper()}")

    else:
        print("❌ Nenhum produto encontrado")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        termo = " ".join(sys.argv[1:])
    else:
        termo = input("Digite o produto que deseja buscar: ")

    if termo.strip():
        testar_scraper(termo.strip())
    else:
        print("❌ Termo de busca inválido")
