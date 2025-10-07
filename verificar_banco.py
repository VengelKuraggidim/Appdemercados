#!/usr/bin/env python3
"""
Script para verificar o conteúdo do banco de dados
"""
from app.models.database import get_db, Produto, Preco

def verificar_banco():
    db = next(get_db())

    total_produtos = db.query(Produto).count()
    total_precos = db.query(Preco).count()
    contribuicoes_manuais = db.query(Preco).filter(Preco.manual == True).count()

    print("=" * 60)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("=" * 60)
    print(f"\n✅ Total de produtos: {total_produtos}")
    print(f"✅ Total de preços: {total_precos}")
    print(f"👥 Contribuições manuais: {contribuicoes_manuais}")
    print(f"🤖 Preços de scraping: {total_precos - contribuicoes_manuais}")

    print(f"\n📁 Arquivo do banco: precos.db")
    print(f"💾 Localização: /home/vengel/PycharmProjects/PythonProject4/precos.db")

    print("\n✅ GARANTIA DE PERSISTÊNCIA:")
    print("   • Dados salvos em arquivo físico (SQLite)")
    print("   • Não depende do cache do navegador")
    print("   • Permanece mesmo após limpar cache/cookies")
    print("   • Backup recomendado do arquivo precos.db")

    # Últimas contribuições
    ultimas = db.query(Preco).filter(Preco.manual == True).order_by(
        Preco.data_coleta.desc()
    ).limit(5).all()

    if ultimas:
        print("\n📋 ÚLTIMAS 5 CONTRIBUIÇÕES:")
        print("-" * 60)
        for p in ultimas:
            print(f"   • {p.produto.nome[:40]:40} - R$ {p.preco:.2f}")
            print(f"     {p.supermercado} | {p.data_coleta.strftime('%d/%m/%Y %H:%M')}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    verificar_banco()
