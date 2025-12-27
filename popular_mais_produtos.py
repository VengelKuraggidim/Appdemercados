#!/usr/bin/env python3
"""
Script para adicionar mais produtos com promoções ao banco
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import SessionLocal, Produto, Preco

def popular():
    db = SessionLocal()

    # Produtos com diferentes supermercados e alguns em promoção
    produtos = [
        {
            "nome": "Leite Integral Parmalat 1L",
            "marca": "Parmalat",
            "categoria": "laticínios",
            "precos": [
                {"supermercado": "Carrefour", "preco": 5.49, "preco_original": 6.99, "em_promocao": True, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 5.89, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 5.99, "lat": -23.547200, "lon": -46.645400},
                {"supermercado": "Atacadão", "preco": 4.99, "preco_original": 5.99, "em_promocao": True, "lat": -23.563600, "lon": -46.654321}
            ]
        },
        {
            "nome": "Macarrão Barilla Penne 500g",
            "marca": "Barilla",
            "categoria": "massas",
            "precos": [
                {"supermercado": "Carrefour", "preco": 8.90, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 9.50, "preco_original": 10.90, "em_promocao": True, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 8.50, "lat": -23.547200, "lon": -46.645400}
            ]
        },
        {
            "nome": "Biscoito Recheado Oreo 144g",
            "marca": "Oreo",
            "categoria": "biscoitos",
            "precos": [
                {"supermercado": "Carrefour", "preco": 4.99, "preco_original": 6.49, "em_promocao": True, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 5.49, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 4.89, "preco_original": 5.99, "em_promocao": True, "lat": -23.547200, "lon": -46.645400},
                {"supermercado": "Mercado Livre", "preco": 5.99, "lat": -23.555555, "lon": -46.642222}
            ]
        },
        {
            "nome": "Refrigerante Coca-Cola 2L",
            "marca": "Coca-Cola",
            "categoria": "bebidas",
            "precos": [
                {"supermercado": "Carrefour", "preco": 7.99, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 8.99, "preco_original": 10.99, "em_promocao": True, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 7.49, "preco_original": 8.99, "em_promocao": True, "lat": -23.547200, "lon": -46.645400},
                {"supermercado": "Atacadão", "preco": 6.99, "lat": -23.563600, "lon": -46.654321}
            ]
        },
        {
            "nome": "Sabão em Pó OMO 1kg",
            "marca": "OMO",
            "categoria": "limpeza",
            "precos": [
                {"supermercado": "Carrefour", "preco": 12.90, "preco_original": 15.90, "em_promocao": True, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 13.50, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 11.90, "preco_original": 14.90, "em_promocao": True, "lat": -23.547200, "lon": -46.645400}
            ]
        },
        {
            "nome": "Papel Higiênico Neve 12 rolos",
            "marca": "Neve",
            "categoria": "higiene",
            "precos": [
                {"supermercado": "Carrefour", "preco": 18.90, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 19.90, "preco_original": 24.90, "em_promocao": True, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 17.90, "preco_original": 21.90, "em_promocao": True, "lat": -23.547200, "lon": -46.645400},
                {"supermercado": "Atacadão", "preco": 16.90, "lat": -23.563600, "lon": -46.654321}
            ]
        },
        {
            "nome": "Iogurte Grego Danone 400g",
            "marca": "Danone",
            "categoria": "laticínios",
            "precos": [
                {"supermercado": "Carrefour", "preco": 7.99, "preco_original": 9.99, "em_promocao": True, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 8.50, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 7.49, "lat": -23.547200, "lon": -46.645400}
            ]
        },
        {
            "nome": "Chocolate Nestlé 90g",
            "marca": "Nestlé",
            "categoria": "doces",
            "precos": [
                {"supermercado": "Carrefour", "preco": 6.99, "lat": -23.550520, "lon": -46.633308},
                {"supermercado": "Pão de Açúcar", "preco": 7.50, "preco_original": 8.90, "em_promocao": True, "lat": -23.561684, "lon": -46.656139},
                {"supermercado": "Extra", "preco": 6.49, "preco_original": 7.99, "em_promocao": True, "lat": -23.547200, "lon": -46.645400},
                {"supermercado": "Mercado Livre", "preco": 7.99, "lat": -23.555555, "lon": -46.642222}
            ]
        }
    ]

    total_produtos = 0
    total_precos = 0
    total_promocoes = 0

    print("\n🛒 Adicionando mais produtos ao banco...")
    print("="*60)

    for p_data in produtos:
        # Criar produto
        produto = Produto(
            nome=p_data["nome"],
            marca=p_data["marca"],
            categoria=p_data["categoria"],
            data_criacao=datetime.now()
        )
        db.add(produto)
        db.flush()

        total_produtos += 1
        print(f"\n✅ {produto.nome}")

        # Adicionar preços
        for preco_data in p_data["precos"]:
            preco = Preco(
                produto_id=produto.id,
                supermercado=preco_data["supermercado"],
                preco=preco_data["preco"],
                preco_original=preco_data.get("preco_original"),
                em_promocao=preco_data.get("em_promocao", False),
                latitude=preco_data.get("lat"),
                longitude=preco_data.get("lon"),
                disponivel=True,
                data_coleta=datetime.now()
            )
            db.add(preco)
            total_precos += 1

            if preco.em_promocao:
                total_promocoes += 1
                economia = preco.preco_original - preco.preco if preco.preco_original else 0
                print(f"   🔥 {preco.supermercado:20} R$ {preco.preco:.2f} (economia: R$ {economia:.2f})")
            else:
                print(f"      {preco.supermercado:20} R$ {preco.preco:.2f}")

    db.commit()

    print("\n" + "="*60)
    print("✅ CONCLUÍDO!")
    print(f"   📦 {total_produtos} produtos adicionados")
    print(f"   💰 {total_precos} preços adicionados")
    print(f"   🔥 {total_promocoes} promoções cadastradas")
    print("="*60 + "\n")

    db.close()

if __name__ == "__main__":
    popular()
