"""
Teste do scraper com comportamento humano
"""
from app.scrapers.scraper_humano import ScraperHumano
import json


def main():
    print("=" * 80)
    print("TESTE DO SCRAPER HUMANO - Comportamento Anti-Detecção")
    print("=" * 80)

    # Criar scraper (headless=False para ver o navegador)
    # Mude para headless=True para rodar sem interface
    scraper = ScraperHumano(headless=False)

    try:
        # Termo de busca
        termo = input("\n🔍 Digite o produto para buscar (ex: arroz, feijão, café): ").strip()

        if not termo:
            termo = "arroz"
            print(f"   Usando termo padrão: {termo}")

        # Escolher mercado
        print("\n📍 Escolha os mercados:")
        print("1. Apenas Carrefour")
        print("2. Apenas Pão de Açúcar")
        print("3. Apenas Extra")
        print("4. Todos")

        opcao = input("Opção (1-4): ").strip()

        mercados = None
        if opcao == "1":
            mercados = ['carrefour']
        elif opcao == "2":
            mercados = ['pao_acucar']
        elif opcao == "3":
            mercados = ['extra']

        # Buscar
        produtos = scraper.buscar_todos(termo, mercados)

        # Exibir resultados
        print("\n" + "=" * 80)
        print("📊 RESULTADOS")
        print("=" * 80)

        if not produtos:
            print("❌ Nenhum produto encontrado")
        else:
            # Agrupar por mercado
            por_mercado = {}
            for p in produtos:
                mercado = p['supermercado']
                if mercado not in por_mercado:
                    por_mercado[mercado] = []
                por_mercado[mercado].append(p)

            for mercado, items in por_mercado.items():
                print(f"\n🏪 {mercado.upper()} - {len(items)} produtos")
                print("-" * 80)

                for i, produto in enumerate(items[:5], 1):  # Mostrar apenas primeiros 5
                    preco_str = f"R$ {produto['preco']:.2f}"

                    if produto.get('preco_original'):
                        desconto = ((produto['preco_original'] - produto['preco']) / produto['preco_original']) * 100
                        preco_str += f" (era R$ {produto['preco_original']:.2f} - {desconto:.0f}% OFF)"

                    print(f"{i}. {produto['nome'][:60]}")
                    print(f"   💰 {preco_str}")
                    if produto['em_promocao']:
                        print(f"   🔥 EM PROMOÇÃO")
                    print()

        # Salvar em arquivo JSON
        output_file = 'resultados_scraping.json'
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
            print(f"Em promoção: {em_promocao} ({em_promocao/len(produtos)*100:.1f}%)")

    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")

    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🔧 Fechando scraper...")
        scraper.close()
        print("✅ Concluído!")


if __name__ == "__main__":
    main()
