"""
Teste do scraper simples (sem Selenium)
Funciona em qualquer ambiente!
"""
from app.scrapers.scraper_simples import scraper_simples
import json


def main():
    print("=" * 80)
    print("🧪 TESTE DO SCRAPER SIMPLES (Requests + BeautifulSoup)")
    print("=" * 80)
    print("\nEste scraper NÃO precisa de Chrome/ChromeDriver!")
    print("Funciona com apenas requests + BeautifulSoup\n")

    try:
        termo = input("🔍 Digite o produto para buscar (ou Enter para 'arroz'): ").strip()
        if not termo:
            termo = "arroz"
            print(f"   Usando: {termo}")

        # Buscar
        produtos = scraper_simples.buscar_todos(termo)

        # Exibir resultados
        if not produtos:
            print("\n⚠️  Nenhum produto encontrado")
        else:
            # Agrupar por mercado
            por_mercado = {}
            for p in produtos:
                mercado = p['supermercado']
                if mercado not in por_mercado:
                    por_mercado[mercado] = []
                por_mercado[mercado].append(p)

            print("\n" + "=" * 80)
            print("📊 RESULTADOS")
            print("=" * 80)

            for mercado, items in por_mercado.items():
                print(f"\n🏪 {mercado.upper()} - {len(items)} produtos")
                print("-" * 80)

                for i, produto in enumerate(items[:5], 1):
                    preco_str = f"R$ {produto['preco']:.2f}"

                    if produto.get('preco_original'):
                        desconto = ((produto['preco_original'] - produto['preco']) / produto['preco_original']) * 100
                        preco_str += f" (era R$ {produto['preco_original']:.2f} - {desconto:.0f}% OFF)"

                    print(f"{i}. {produto['nome'][:70]}")
                    print(f"   💰 {preco_str}")
                    if produto['em_promocao']:
                        print(f"   🔥 EM PROMOÇÃO")
                    print()

            # Salvar JSON
            output_file = 'resultados_scraping_simples.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(produtos, f, ensure_ascii=False, indent=2)

            print(f"\n💾 Resultados salvos em: {output_file}")

            # Estatísticas
            print("\n" + "=" * 80)
            print("📈 ESTATÍSTICAS")
            print("=" * 80)
            print(f"Total de produtos: {len(produtos)}")
            print(f"Mercados consultados: {len(por_mercado)}")

            if produtos:
                precos = [p['preco'] for p in produtos]
                print(f"Preço mínimo: R$ {min(precos):.2f}")
                print(f"Preço máximo: R$ {max(precos):.2f}")
                print(f"Preço médio: R$ {sum(precos)/len(precos):.2f}")

                em_promocao = len([p for p in produtos if p['em_promocao']])
                if em_promocao > 0:
                    print(f"Em promoção: {em_promocao} ({em_promocao/len(produtos)*100:.1f}%)")

    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")

    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n✅ Teste concluído!")


if __name__ == "__main__":
    main()
