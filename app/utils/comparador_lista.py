"""
Comparador de Lista de Compras
Encontra o melhor supermercado para comprar todos os itens da lista
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from statistics import mean
import math

from app.models.database import Preco, Produto, ItemLista


class ComparadorLista:
    """Compara precos da lista de compras entre supermercados"""

    # Peso da distancia no calculo (R$ por km)
    PESO_DISTANCIA_KM = 2.0

    # Bonus por disponibilidade (pontos)
    BONUS_DISPONIBILIDADE = 10.0

    # Dias para considerar precos
    DIAS_PRECOS = 30

    def __init__(self, db: Session):
        self.db = db

    def comparar_lista(
        self,
        itens: List[ItemLista],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        distancia_maxima_km: float = 10.0
    ) -> Dict:
        """
        Compara lista de compras entre todos os supermercados.
        Retorna o melhor supermercado considerando preco total + distancia.
        """
        if not itens:
            return {
                'supermercados': [],
                'melhor_supermercado': None,
                'economia_potencial': 0
            }

        supermercados_totais = {}  # {supermercado: {total, itens, distancia}}
        itens_nao_comprados = [item for item in itens if not item.comprado]

        for item in itens_nao_comprados:
            # Busca precos para este item
            precos = self._buscar_precos_item(item.nome_produto)

            for preco in precos:
                supermercado = preco.supermercado

                if supermercado not in supermercados_totais:
                    supermercados_totais[supermercado] = {
                        'nome': supermercado,
                        'total': 0.0,
                        'itens': [],
                        'itens_disponiveis': 0,
                        'latitude': preco.latitude,
                        'longitude': preco.longitude,
                        'endereco': preco.endereco,
                        'distancia_km': None
                    }

                # Verifica se ja adicionou este item para este supermercado
                itens_adicionados = [i['nome'] for i in supermercados_totais[supermercado]['itens']]
                if item.nome_produto in itens_adicionados:
                    continue

                # Adiciona preco do item
                item_total = preco.preco * item.quantidade
                supermercados_totais[supermercado]['itens'].append({
                    'nome': item.nome_produto,
                    'preco_unitario': preco.preco,
                    'quantidade': item.quantidade,
                    'subtotal': item_total
                })
                supermercados_totais[supermercado]['total'] += item_total
                supermercados_totais[supermercado]['itens_disponiveis'] += 1

        # Calcula distancias se localizacao do usuario foi fornecida
        if latitude and longitude:
            for sup in supermercados_totais.values():
                if sup.get('latitude') and sup.get('longitude'):
                    sup['distancia_km'] = self._calcular_distancia(
                        latitude, longitude,
                        sup['latitude'], sup['longitude']
                    )

        # Converte para lista e ordena
        supermercados_lista = list(supermercados_totais.values())
        total_itens = len(itens_nao_comprados)

        # Ordena por score (menor eh melhor)
        supermercados_lista.sort(
            key=lambda x: self._calcular_score(x, total_itens)
        )

        # Encontra melhor opcao
        melhor = supermercados_lista[0] if supermercados_lista else None

        # Calcula economia potencial
        economia = 0.0
        if len(supermercados_lista) > 1:
            economia = supermercados_lista[-1]['total'] - supermercados_lista[0]['total']

        return {
            'supermercados': supermercados_lista,
            'melhor_supermercado': melhor,
            'economia_potencial': economia,
            'total_itens': total_itens
        }

    def _buscar_precos_item(self, nome_produto: str) -> List[Preco]:
        """Busca precos para um produto nos ultimos 30 dias"""
        data_limite = datetime.now() - timedelta(days=self.DIAS_PRECOS)

        # Busca por nome similar
        return self.db.query(Preco).join(Produto).filter(
            Produto.nome.ilike(f"%{nome_produto}%"),
            Preco.data_coleta >= data_limite,
            Preco.disponivel == True,
            Preco.preco > 0
        ).order_by(Preco.preco.asc()).all()

    def _calcular_distancia(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calcula distancia entre dois pontos em km (formula de Haversine)"""
        R = 6371  # Raio da Terra em km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _calcular_score(self, supermercado: Dict, total_itens: int) -> float:
        """
        Calcula score para ranking de supermercados.
        Score menor = melhor opcao.

        Score = preco_total + (distancia * peso) - (bonus_disponibilidade)
        """
        score = supermercado['total']

        # Penalidade por distancia (R$ 2 por km)
        if supermercado.get('distancia_km'):
            score += supermercado['distancia_km'] * self.PESO_DISTANCIA_KM

        # Bonus por disponibilidade de itens
        if total_itens > 0:
            disponibilidade = supermercado['itens_disponiveis'] / total_itens
            score -= disponibilidade * self.BONUS_DISPONIBILIDADE

        return score

    def atualizar_melhores_precos(self, lista_id: int) -> None:
        """Atualiza cache de melhores precos para cada item da lista"""
        from app.models.database import ListaCompras

        lista = self.db.query(ListaCompras).filter(ListaCompras.id == lista_id).first()
        if not lista:
            return

        for item in lista.itens:
            if item.comprado:
                continue

            precos = self._buscar_precos_item(item.nome_produto)
            if precos:
                melhor = precos[0]  # Ja ordenado por preco
                item.melhor_preco = melhor.preco
                item.melhor_supermercado = melhor.supermercado
                item.data_comparacao = datetime.now()

        self.db.commit()


def get_comparador_lista(db: Session) -> ComparadorLista:
    """Factory para criar instancia do ComparadorLista"""
    return ComparadorLista(db)
