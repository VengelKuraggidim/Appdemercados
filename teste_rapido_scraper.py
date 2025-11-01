"""
Teste rápido do scraper humano
"""
from app.scrapers.scraper_humano import ScraperHumano


def main():
    print("🧪 Teste rápido do Scraper Humano\n")

    scraper = ScraperHumano(headless=True)  # headless para ser mais rápido

    try:
        print("📍 Testando Carrefour com produto: arroz\n")
        produtos = scraper.buscar_carrefour("arroz")

        if produtos:
            print(f"\n✅ SUCESSO! Encontrados {len(produtos)} produtos:")
            for i, p in enumerate(produtos[:3], 1):
                print(f"{i}. {p['nome'][:50]} - R$ {p['preco']:.2f}")
        else:
            print("\n⚠️  Nenhum produto encontrado - mas o scraper rodou sem erros!")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scraper.close()
        print("\n✅ Teste concluído!")


if __name__ == "__main__":
    main()
