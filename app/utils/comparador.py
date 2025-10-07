from typing import List, Dict
from app.models.database import Preco


class Comparador:
    """Utility class for comparing prices"""

    def comparar_precos(self, precos: List[Preco]) -> Dict:
        """
        Compare prices and return analysis
        """
        if not precos:
            return {
                "erro": "Nenhum preço disponível para comparação"
            }

        # Sort by price
        precos_ordenados = sorted(precos, key=lambda p: p.preco)

        melhor_preco = precos_ordenados[0]
        pior_preco = precos_ordenados[-1]

        # Calculate savings
        diferenca_absoluta = pior_preco.preco - melhor_preco.preco
        diferenca_percentual = ((pior_preco.preco - melhor_preco.preco) / pior_preco.preco) * 100

        # Group by supermarket
        por_supermercado = {}
        for preco in precos:
            mercado = preco.supermercado.value
            if mercado not in por_supermercado:
                por_supermercado[mercado] = []
            por_supermercado[mercado].append({
                'preco': preco.preco,
                'em_promocao': preco.em_promocao,
                'url': preco.url,
                'data_coleta': preco.data_coleta.isoformat()
            })

        # Calculate average price
        preco_medio = sum(p.preco for p in precos) / len(precos)

        return {
            'produto': {
                'id': melhor_preco.produto_id,
                'nome': melhor_preco.produto.nome,
                'marca': melhor_preco.produto.marca
            },
            'melhor_preco': {
                'valor': melhor_preco.preco,
                'supermercado': melhor_preco.supermercado.value,
                'url': melhor_preco.url,
                'em_promocao': melhor_preco.em_promocao,
                'data_coleta': melhor_preco.data_coleta.isoformat()
            },
            'pior_preco': {
                'valor': pior_preco.preco,
                'supermercado': pior_preco.supermercado.value
            },
            'economia': {
                'valor_absoluto': round(diferenca_absoluta, 2),
                'percentual': round(diferenca_percentual, 2)
            },
            'preco_medio': round(preco_medio, 2),
            'total_comparacoes': len(precos),
            'por_supermercado': por_supermercado
        }

    def encontrar_melhor_combinacao(self, lista_produtos: List[str]) -> Dict:
        """
        Find the best combination of supermarkets for a shopping list
        """
        # This would implement logic to find optimal shopping strategy
        # For now, return placeholder
        return {
            "status": "Em desenvolvimento",
            "message": "Funcionalidade de otimização de lista de compras em desenvolvimento"
        }
