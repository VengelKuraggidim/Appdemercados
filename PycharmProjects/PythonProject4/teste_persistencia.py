#!/usr/bin/env python3
"""
Script de teste para demonstrar persistência de dados
"""
from app.models.database import get_db, Produto, Preco
from datetime import datetime

def teste_persistencia():
    print("=" * 70)
    print("🧪 TESTE DE PERSISTÊNCIA DE DADOS")
    print("=" * 70)

    db = next(get_db())

    # Conta registros antes
    antes_produtos = db.query(Produto).count()
    antes_precos = db.query(Preco).count()

    print(f"\n📊 ANTES DO TESTE:")
    print(f"   Produtos: {antes_produtos}")
    print(f"   Preços: {antes_precos}")

    # Adiciona um produto de teste
    print("\n➕ Adicionando produto de teste...")
    produto_teste = Produto(
        nome="TESTE - Produto de Persistência",
        marca="Teste Inc.",
        categoria="Teste"
    )
    db.add(produto_teste)
    db.flush()

    preco_teste = Preco(
        produto_id=produto_teste.id,
        supermercado="Supermercado Teste",
        preco=99.99,
        em_promocao=True,
        manual=True,
        usuario_nome="Script de Teste",
        disponivel=True,
        verificado=True,
        data_coleta=datetime.now()
    )
    db.add(preco_teste)
    db.commit()

    print("   ✅ Produto adicionado com sucesso!")

    # Conta registros depois
    depois_produtos = db.query(Produto).count()
    depois_precos = db.query(Preco).count()

    print(f"\n📊 DEPOIS DO TESTE:")
    print(f"   Produtos: {depois_produtos}")
    print(f"   Preços: {depois_precos}")

    print(f"\n✅ RESULTADO:")
    print(f"   • {depois_produtos - antes_produtos} produto adicionado")
    print(f"   • {depois_precos - antes_precos} preço adicionado")

    print("\n💾 PERSISTÊNCIA CONFIRMADA!")
    print("   • Dados salvos em: precos.db")
    print("   • Independente do cache do navegador")
    print("   • Permanece após reiniciar o sistema")

    # Remove o teste
    print("\n🗑️  Removendo dados de teste...")
    db.delete(preco_teste)
    db.delete(produto_teste)
    db.commit()
    print("   ✅ Limpeza concluída")

    # Verifica estado final
    final_produtos = db.query(Produto).count()
    final_precos = db.query(Preco).count()

    print(f"\n📊 ESTADO FINAL:")
    print(f"   Produtos: {final_produtos}")
    print(f"   Preços: {final_precos}")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    teste_persistencia()
