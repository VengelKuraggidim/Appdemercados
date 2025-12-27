#!/usr/bin/env python3
"""
Script para popular o banco com produtos básicos de supermercado
"""
from app.models.database import get_db, Produto, Preco
from datetime import datetime

def popular_produtos_basicos():
    """Adiciona produtos básicos ao banco de dados"""
    db = next(get_db())

    produtos_basicos = [
        # Arroz
        {
            'nome': 'Arroz Branco Tipo 1 - 5kg',
            'marca': 'Tio João',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 24.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 26.50, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 23.90, 'em_promocao': True},
            ]
        },
        {
            'nome': 'Arroz Integral Orgânico - 1kg',
            'marca': 'Camil',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 12.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 13.50, 'em_promocao': False},
            ]
        },
        {
            'nome': 'Arroz Parboilizado - 5kg',
            'marca': 'Uncle Ben\'s',
            'precos': [
                {'supermercado': 'Extra', 'preco': 28.90, 'em_promocao': False},
                {'supermercado': 'Mercado Livre', 'preco': 27.50, 'em_promocao': True},
            ]
        },
        # Feijão
        {
            'nome': 'Feijão Carioca - 1kg',
            'marca': 'Camil',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 8.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 9.50, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 8.50, 'em_promocao': True},
            ]
        },
        {
            'nome': 'Feijão Preto - 1kg',
            'marca': 'Kicaldo',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 9.90, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 8.90, 'em_promocao': True},
            ]
        },
        # Açúcar
        {
            'nome': 'Açúcar Cristal - 1kg',
            'marca': 'União',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 4.50, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 4.90, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 3.90, 'em_promocao': True},
            ]
        },
        # Óleo
        {
            'nome': 'Óleo de Soja - 900ml',
            'marca': 'Liza',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 6.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 7.50, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 6.50, 'em_promocao': True},
            ]
        },
        # Café
        {
            'nome': 'Café Torrado e Moído Tradicional - 500g',
            'marca': 'Pilão',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 15.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 16.50, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 14.90, 'em_promocao': True},
            ]
        },
        # Leite
        {
            'nome': 'Leite UHT Integral - 1L',
            'marca': 'Itambé',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 5.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 6.20, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 5.50, 'em_promocao': True},
            ]
        },
        # Macarrão
        {
            'nome': 'Macarrão Espaguete - 500g',
            'marca': 'Barilla',
            'precos': [
                {'supermercado': 'Carrefour', 'preco': 5.90, 'em_promocao': False},
                {'supermercado': 'Pão de Açúcar', 'preco': 6.50, 'em_promocao': False},
                {'supermercado': 'Extra', 'preco': 5.50, 'em_promocao': True},
            ]
        },
    ]

    print("🛒 Populando banco de dados com produtos básicos...")
    print("=" * 60)

    total_produtos = 0
    total_precos = 0

    for item in produtos_basicos:
        # Cria o produto
        produto = Produto(
            nome=item['nome'],
            marca=item['marca'],
            categoria='Alimentos'
        )
        db.add(produto)
        db.flush()

        total_produtos += 1
        print(f"\n✓ Produto criado: {item['nome']}")

        # Adiciona os preços
        for preco_data in item['precos']:
            preco = Preco(
                produto_id=produto.id,
                supermercado=preco_data['supermercado'],
                preco=preco_data['preco'],
                em_promocao=preco_data['em_promocao'],
                manual=True,
                usuario_nome='Sistema',
                disponivel=True,
                verificado=True,
                data_coleta=datetime.now()
            )
            db.add(preco)
            total_precos += 1

            promo_tag = "🔥" if preco_data['em_promocao'] else "  "
            print(f"  {promo_tag} {preco_data['supermercado']:20} - R$ {preco_data['preco']:.2f}")

    db.commit()

    print("\n" + "=" * 60)
    print(f"✅ Banco populado com sucesso!")
    print(f"   • {total_produtos} produtos adicionados")
    print(f"   • {total_precos} preços cadastrados")
    print("\n🔍 Você já pode buscar por produtos como:")
    print("   • arroz")
    print("   • feijão")
    print("   • café")
    print("   • açúcar")
    print("=" * 60)

if __name__ == "__main__":
    popular_produtos_basicos()
