from typing import List, Dict
import requests
import time


class MercadoLivreScraper:
    """Scraper for Mercado Livre using official API"""

    def __init__(self):
        self.api_url = "https://api.mercadolibre.com"
        self.site_id = "MLB"  # Brasil

    def get_supermercado_name(self) -> str:
        return "Mercado Livre"

    def search(self, termo: str) -> List[Dict]:
        """Search for products on Mercado Livre using official API"""
        try:
            # Buscar apenas em categorias de supermercado/alimentos
            categorias_alimentos = [
                "MLB1403",  # Alimentos e Bebidas
                "MLB1576",  # Casa, Móveis e Decoração
            ]

            todos_produtos = []

            for categoria in categorias_alimentos:
                time.sleep(0.5)  # Rate limiting

                # API endpoint para busca
                url = f"{self.api_url}/sites/{self.site_id}/search"
                params = {
                    'q': termo,
                    'category': categoria,
                    'limit': 20,
                    'offset': 0
                }

                response = requests.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    continue

                data = response.json()
                results = data.get('results', [])

                for item in results:
                    try:
                        # Verificar se é frete grátis ou promoção
                        shipping = item.get('shipping', {})
                        em_promocao = shipping.get('free_shipping', False)

                        # Pegar preço original se houver
                        preco_original = None
                        if 'original_price' in item and item['original_price']:
                            preco_original = item['original_price']
                            em_promocao = True

                        produto = {
                            'nome': item.get('title', '').strip(),
                            'marca': None,  # ML API não retorna marca diretamente
                            'preco': float(item.get('price', 0)),
                            'preco_original': preco_original,
                            'em_promocao': em_promocao,
                            'url': item.get('permalink', ''),
                            'supermercado': self.get_supermercado_name(),
                            'disponivel': item.get('available_quantity', 0) > 0,
                            'thumbnail': item.get('thumbnail', '')
                        }

                        # Só adicionar se tiver preço válido
                        if produto['preco'] > 0:
                            todos_produtos.append(produto)

                    except Exception as e:
                        print(f"Erro ao processar item do Mercado Livre: {e}")
                        continue

                # Limitar a primeira categoria se já tiver resultados
                if todos_produtos:
                    break

            # Remover duplicatas e limitar a 20 produtos
            produtos_unicos = {}
            for p in todos_produtos:
                if p['nome'] not in produtos_unicos:
                    produtos_unicos[p['nome']] = p

            return list(produtos_unicos.values())[:20]

        except Exception as e:
            print(f"Erro na API do Mercado Livre: {e}")
            return []
