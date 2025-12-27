#!/usr/bin/env python3
"""
Popular banco de dados com dados de demonstração
"""

from app.models.database import SessionLocal, init_db, Produto, Preco, SupermercadoEnum
from datetime import datetime, timedelta
import random

# Initialize database
init_db()
db = SessionLocal()

# Produtos de exemplo
produtos_demo = [
    {
        "nome": "Arroz Branco Tipo 1 5kg",
        "marca": "Tio João",
        "categoria": "Arroz",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 23.90, "em_promocao": False},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 25.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 22.90, "em_promocao": True},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 24.80, "em_promocao": False},
        ]
    },
    {
        "nome": "Feijão Carioca Tipo 1 1kg",
        "marca": "Camil",
        "categoria": "Feijão",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 7.90, "em_promocao": True},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 8.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 8.20, "em_promocao": False},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 9.00, "em_promocao": False},
        ]
    },
    {
        "nome": "Café Torrado e Moído 500g",
        "marca": "Pilão",
        "categoria": "Café",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 15.90, "em_promocao": False},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 14.90, "em_promocao": True},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 16.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 15.50, "em_promocao": False},
        ]
    },
    {
        "nome": "Açúcar Cristal 1kg",
        "marca": "União",
        "categoria": "Açúcar",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 4.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 4.90, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 4.20, "em_promocao": True},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 5.00, "em_promocao": False},
        ]
    },
    {
        "nome": "Óleo de Soja 900ml",
        "marca": "Liza",
        "categoria": "Óleo",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 8.90, "em_promocao": True},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 9.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 9.20, "em_promocao": False},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 10.00, "em_promocao": False},
        ]
    },
    {
        "nome": "Macarrão Espaguete 500g",
        "marca": "Barilla",
        "categoria": "Massas",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 6.90, "em_promocao": False},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 7.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 6.50, "em_promocao": True},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 7.80, "em_promocao": False},
        ]
    },
    {
        "nome": "Leite Integral 1L",
        "marca": "Italac",
        "categoria": "Laticínios",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 5.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 5.90, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 5.20, "em_promocao": True},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 6.00, "em_promocao": False},
        ]
    },
    {
        "nome": "Sal Refinado 1kg",
        "marca": "Cisne",
        "categoria": "Temperos",
        "precos": [
            {"supermercado": SupermercadoEnum.CARREFOUR, "preco": 2.50, "em_promocao": False},
            {"supermercado": SupermercadoEnum.PAO_ACUCAR, "preco": 2.80, "em_promocao": False},
            {"supermercado": SupermercadoEnum.EXTRA, "preco": 2.30, "em_promocao": True},
            {"supermercado": SupermercadoEnum.MERCADO_LIVRE, "preco": 2.90, "em_promocao": False},
        ]
    },
]

print("🗑️  Limpando banco de dados anterior...")
db.query(Preco).delete()
db.query(Produto).delete()
db.commit()

print("📦 Populando banco de dados com produtos de demonstração...")

for item in produtos_demo:
    # Criar produto
    produto = Produto(
        nome=item["nome"],
        marca=item["marca"],
        categoria=item["categoria"],
        data_criacao=datetime.now()
    )
    db.add(produto)
    db.flush()

    # Adicionar preços atuais
    for preco_info in item["precos"]:
        preco = Preco(
            produto_id=produto.id,
            supermercado=preco_info["supermercado"],
            preco=preco_info["preco"],
            em_promocao=preco_info["em_promocao"],
            url=f"https://example.com/produto/{produto.id}",
            disponivel=True,
            data_coleta=datetime.now()
        )
        db.add(preco)

    # Adicionar histórico (últimos 7 dias)
    for dias in range(1, 8):
        data_passada = datetime.now() - timedelta(days=dias)
        for preco_info in item["precos"]:
            # Varia o preço um pouco
            variacao = random.uniform(-0.5, 0.5)
            preco_historico = Preco(
                produto_id=produto.id,
                supermercado=preco_info["supermercado"],
                preco=round(preco_info["preco"] + variacao, 2),
                em_promocao=random.choice([True, False]),
                url=f"https://example.com/produto/{produto.id}",
                disponivel=True,
                data_coleta=data_passada
            )
            db.add(preco_historico)

    print(f"  ✓ {produto.nome}")

db.commit()

print(f"\n✅ Banco de dados populado com sucesso!")
print(f"   • {len(produtos_demo)} produtos")
print(f"   • {len(produtos_demo) * 4} preços atuais")
print(f"   • {len(produtos_demo) * 4 * 7} registros de histórico")
print(f"\n🌐 Agora você pode testar em: http://localhost:3000")
print(f"   Busque por: arroz, feijão, café, açúcar, óleo, etc.")

db.close()
