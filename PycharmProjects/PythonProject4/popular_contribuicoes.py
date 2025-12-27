#!/usr/bin/env python3
"""
Popular banco com contribuições de exemplo
"""

import requests

API_URL = "http://localhost:8000"

contribuicoes = [
    {
        "produto_nome": "Arroz Tio João 5kg",
        "produto_marca": "Tio João",
        "supermercado": "Carrefour",
        "preco": 22.90,
        "em_promocao": True,
        "localizacao": "São Paulo - Centro",
        "usuario_nome": "Maria Santos"
    },
    {
        "produto_nome": "Feijão Carioca Camil 1kg",
        "produto_marca": "Camil",
        "supermercado": "Pão de Açúcar",
        "preco": 7.50,
        "em_promocao": False,
        "localizacao": "Rio de Janeiro - Copacabana",
        "usuario_nome": "Pedro Lima"
    },
    {
        "produto_nome": "Café Pilão 500g",
        "produto_marca": "Pilão",
        "supermercado": "Extra",
        "preco": 14.90,
        "em_promocao": True,
        "localizacao": "Belo Horizonte - Savassi",
        "usuario_nome": "Ana Costa"
    },
    {
        "produto_nome": "Açúcar União 1kg",
        "produto_marca": "União",
        "supermercado": "Supermercado Nacional",
        "preco": 4.50,
        "em_promocao": False,
        "localizacao": "Curitiba - Centro",
        "usuario_nome": "Carlos Souza"
    },
    {
        "produto_nome": "Óleo Liza 900ml",
        "produto_marca": "Liza",
        "supermercado": "Carrefour",
        "preco": 8.90,
        "em_promocao": True,
        "localizacao": "Porto Alegre - Zona Sul",
        "usuario_nome": "Juliana Oliveira"
    },
    {
        "produto_nome": "Leite Italac 1L",
        "produto_marca": "Italac",
        "supermercado": "Atacadão",
        "preco": 5.20,
        "em_promocao": False,
        "localizacao": "Salvador - Pituba",
        "usuario_nome": "Roberto Alves"
    },
    {
        "produto_nome": "Macarrão Barilla 500g",
        "produto_marca": "Barilla",
        "supermercado": "Pão de Açúcar",
        "preco": 6.90,
        "em_promocao": False,
        "localizacao": "Brasília - Asa Sul",
        "usuario_nome": "Fernanda Rocha"
    },
    {
        "produto_nome": "Arroz Tio João 5kg",
        "produto_marca": "Tio João",
        "supermercado": "Extra",
        "preco": 21.90,
        "em_promocao": True,
        "localizacao": "São Paulo - Paulista",
        "usuario_nome": "Lucas Martins"
    },
]

print("🛒 Adicionando contribuições de exemplo...\n")

for contrib in contribuicoes:
    try:
        response = requests.post(f"{API_URL}/api/contribuir", json=contrib)
        if response.status_code == 200:
            print(f"✓ {contrib['produto_nome']} - R$ {contrib['preco']:.2f} ({contrib['supermercado']})")
        else:
            print(f"✗ Erro ao adicionar {contrib['produto_nome']}: {response.text}")
    except Exception as e:
        print(f"✗ Erro de conexão: {e}")

print("\n✅ Contribuições adicionadas!")
print(f"\n🌐 Acesse:")
print(f"   • Buscar: http://localhost:3000")
print(f"   • Contribuir: http://localhost:3000/contribuir.html")
print(f"   • Ver contribuições: http://localhost:3000/contribuicoes.html")
