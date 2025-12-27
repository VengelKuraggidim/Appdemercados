"""
Teste do Sistema Unificado de Scraping
Testa todas as estratégias implementadas
"""
from app.scrapers.scraper_unificado import scraper_unificado
import json
import time


def main():
    print("=" * 80)
    print("🧪 TESTE DO SCRAPER UNIFICADO INTELIGENTE")
    print("=" * 80)
    print("\nEste sistema tenta múltiplas estratégias até conseguir resultados:")
    print("1️⃣  APIs Públicas (Mercado Livre, Americanas, Shopee)")
    print("2️⃣  Playwright (navegador moderno)")
    print("3️⃣  Selenium Anti-Detecção")
    print("4️⃣  Requests Simples\n")

    try:
        termo = input("🔍 Digite o produto para buscar (ou Enter para 'arroz'): ").strip()
        if not termo:
            termo = "arroz"
            print(f"   Usando: {termo}")

        # Escolher modo
        print("\n📋 Escolha o modo:")
        print("1. Busca Rápida (apenas APIs)")
        print("2. Busca Inteligente (para com 5 produtos)")
        print("3. Busca Completa (para com 10 produtos)")
        print("4. Busca Exaustiva (todas as estratégias)")

        modo = input("Modo (1-4, padrão=2): ").strip() or "2"

        start_time = time.time()

        if modo == "1":
            print("\n⚡ Modo: Busca Rápida")
            produtos = scraper_unificado.buscar_rapido(termo)
        elif modo == "2":
            print("\n🧠 Modo: Busca Inteligente (mínimo 5 produtos)")
            produtos = scraper_unificado.buscar_inteligente(termo, minimo_produtos=5)
        elif modo == "3":
            print("\n🎯 Modo: Busca Completa (mínimo 10 produtos)")
            produtos = scraper_unificado.buscar_completo(termo)
        else:
            print("\n🔥 Modo: Busca Exaustiva (todas as estratégias)")
            produtos = scraper_unificado.buscar_inteligente(termo, minimo_produtos=50)

        elapsed = time.time() - start_time

        # Exibir resultados
        if not produtos:
            print("\n" + "=" * 80)
            print("❌ NENHUM PRODUTO ENCONTRADO")
            print("=" * 80)
            print("\n💡 Dicas:")
            print("- Tente outro termo de busca")
            print("- Verifique sua conexão com a internet")
            print("- Os sites podem estar bloqueando temporariamente")
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
                    if produto.get('em_promocao'):
                        print(f"   🔥 EM PROMOÇÃO")
                    if produto.get('url'):
                        print(f"   🔗 {produto['url'][:60]}...")
                    print()

                if len(items) > 5:
                    print(f"   ... e mais {len(items) - 5} produtos\n")

            # Salvar JSON
            output_file = 'resultados_scraper_unificado.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(produtos, f, ensure_ascii=False, indent=2)

            print(f"💾 Resultados salvos em: {output_file}")

            # Estatísticas
            print("\n" + "=" * 80)
            print("📈 ESTATÍSTICAS")
            print("=" * 80)
            print(f"⏱️  Tempo total: {elapsed:.2f}s")
            print(f"📦 Total de produtos: {len(produtos)}")
            print(f"🏪 Mercados consultados: {len(por_mercado)}")

            if produtos:
                precos = [p['preco'] for p in produtos if p.get('preco', 0) > 0]
                if precos:
                    print(f"💰 Preço mínimo: R$ {min(precos):.2f}")
                    print(f"💰 Preço máximo: R$ {max(precos):.2f}")
                    print(f"💰 Preço médio: R$ {sum(precos)/len(precos):.2f}")

                em_promocao = len([p for p in produtos if p.get('em_promocao')])
                if em_promocao > 0:
                    print(f"🔥 Em promoção: {em_promocao} ({em_promocao/len(produtos)*100:.1f}%)")

            # Distribuição por mercado
            print(f"\n📊 Distribuição:")
            for mercado, items in sorted(por_mercado.items(), key=lambda x: len(x[1]), reverse=True):
                barra = "█" * (len(items) // 2)
                print(f"   {mercado:15s} [{len(items):2d}] {barra}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")

    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🔧 Fechando scrapers...")
        scraper_unificado.close_all()
        print("✅ Teste concluído!")


if __name__ == "__main__":
    main()
