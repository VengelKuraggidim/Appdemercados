#!/usr/bin/env python3
"""
Debug da API do Mercado Livre
"""
import requests
import json

# Testar API diretamente
url = "https://api.mercadolibre.com/sites/MLB/search"
params = {
    'q': 'arroz',
    'limit': 5
}

print("🔍 Testando API do Mercado Livre...")
print(f"URL: {url}")
print(f"Params: {params}\n")

response = requests.get(url, params=params, timeout=10)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\nTotal de resultados: {data.get('paging', {}).get('total', 0)}")
    print(f"Resultados retornados: {len(data.get('results', []))}\n")

    for i, item in enumerate(data.get('results', [])[:3], 1):
        print(f"\n{i}. {item.get('title')}")
        print(f"   Preço: R$ {item.get('price')}")
        print(f"   Vendedor: {item.get('seller', {}).get('nickname', 'N/A')}")
        print(f"   Condição: {item.get('condition')}")
        print(f"   Categoria: {item.get('category_id')}")
        print(f"   Link: {item.get('permalink')}")
else:
    print(f"Erro: {response.text}")
