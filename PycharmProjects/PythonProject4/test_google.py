#!/usr/bin/env python3
"""
Teste do Google Shopping Scraper
"""

from app.scrapers.google_shopping import GoogleShoppingScraper

def testar_google(termo: str):
    print(f"\n{'='*60}")
    print(f"🔍 TESTANDO GOOGLE SHOPPING")
    print(f"Termo: {termo}")
    print(f"{'='*60}\n")

    scraper = GoogleShoppingScraper()
    produtos = scraper.search(termo)

    if produtos:
        print(f"\n✅ SUCESSO! Encontrados {len(produtos)} produtos")
        print(f"\n{'='*60}")
        print("📊 RESULTADOS:")
        print(f"{'='*60}\n")

        # Agrupa por supermercado
        por_mercado = {}
        for p in produtos:
            mercado = p['supermercado']
            if mercado not in por_mercado:
                por_mercado[mercado] = []
            por_mercado[mercado].append(p)

        # Mostra resultados
        for mercado, items in sorted(por_mercado.items()):
            print(f"\n🏪 {mercado.upper().replace('_', ' ')}: {len(items)} produtos")
            for i, item in enumerate(items[:5], 1):  # Mostra até 5 por mercado
                promo = "🔥 " if item['em_promocao'] else ""
                print(f"   {i}. {promo}R$ {item['preco']:.2f} - {item['nome'][:60]}")
                if item.get('marca'):
                    print(f"      Marca: {item['marca']}")

        # Melhor preço
        melhor = min(produtos, key=lambda x: x['preco'])
        print(f"\n{'='*60}")
        print(f"💰 MELHOR PREÇO ENCONTRADO:")
        print(f"{'='*60}")
        print(f"   R$ {melhor['preco']:.2f}")
        print(f"   {melhor['nome']}")
        print(f"   Loja: {melhor['supermercado'].replace('_', ' ').title()}")
        if melhor.get('url'):
            print(f"   URL: {melhor['url'][:80]}...")
        print(f"{'='*60}\n")

    else:
        print("\n❌ NENHUM PRODUTO ENCONTRADO")
        print("\nPossíveis motivos:")
        print("  • Google está bloqueando requisições automatizadas")
        print("  • Termo de busca não retornou produtos")
        print("  • Estrutura HTML do Google mudou")
        print("\nTente:")
        print("  • Usar um termo mais específico")
        print("  • Executar novamente depois de alguns minutos")
        print("  • Verificar se o Google está acessível\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        termo = " ".join(sys.argv[1:])
    else:
        termo = "arroz 5kg"

    testar_google(termo)
