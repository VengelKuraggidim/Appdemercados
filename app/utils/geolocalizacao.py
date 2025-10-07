"""
Módulo para cálculos de geolocalização e análise de custo-benefício
"""
import math
from typing import Tuple, List, Dict, Optional


class GeoLocalizacao:
    """Classe para cálculos de geolocalização e distância"""

    # Raio da Terra em km
    RAIO_TERRA_KM = 6371.0

    @staticmethod
    def calcular_distancia(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calcula a distância entre duas coordenadas usando a fórmula de Haversine

        Args:
            lat1: Latitude do ponto 1
            lon1: Longitude do ponto 1
            lat2: Latitude do ponto 2
            lon2: Longitude do ponto 2

        Returns:
            Distância em quilômetros
        """
        # Converte graus para radianos
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Diferenças
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Fórmula de Haversine
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        # Distância em km
        distancia = GeoLocalizacao.RAIO_TERRA_KM * c

        return distancia


class AnalisadorCustoBeneficio:
    """Analisa se vale a pena ir a um supermercado mais distante baseado na economia"""

    # Configurações padrão (podem ser personalizadas pelo usuário)
    CUSTO_KM_CARRO = 0.80  # R$/km (combustível + desgaste)
    CUSTO_KM_MOTO = 0.35   # R$/km
    CUSTO_KM_ONIBUS = 0.25 # R$/km (considerando passagem)
    CUSTO_KM_APE = 0.00    # R$/km (grátis!)

    # Valor do tempo (em R$/hora) - opcional
    VALOR_TEMPO_HORA = 15.00  # Salário mínimo/hora aproximado
    VELOCIDADE_MEDIA_URBANA = 30  # km/h

    def __init__(
        self,
        tipo_transporte: str = "carro",
        considerar_tempo: bool = True,
        custo_km_customizado: Optional[float] = None
    ):
        """
        Inicializa o analisador

        Args:
            tipo_transporte: "carro", "moto", "onibus", ou "customizado"
            considerar_tempo: Se deve considerar o valor do tempo gasto
            custo_km_customizado: Custo por km customizado (se tipo_transporte = "customizado")
        """
        self.tipo_transporte = tipo_transporte
        self.considerar_tempo = considerar_tempo

        if tipo_transporte == "customizado" and custo_km_customizado:
            self.custo_por_km = custo_km_customizado
        elif tipo_transporte == "moto":
            self.custo_por_km = self.CUSTO_KM_MOTO
        elif tipo_transporte == "onibus":
            self.custo_por_km = self.CUSTO_KM_ONIBUS
        elif tipo_transporte == "ape":
            self.custo_por_km = self.CUSTO_KM_APE
        else:  # carro (padrão)
            self.custo_por_km = self.CUSTO_KM_CARRO

    def calcular_custo_deslocamento(
        self,
        distancia_km: float,
        ida_e_volta: bool = True
    ) -> Dict[str, float]:
        """
        Calcula o custo total do deslocamento

        Args:
            distancia_km: Distância em quilômetros
            ida_e_volta: Se True, considera ida e volta (distância x2)

        Returns:
            Dicionário com custos detalhados
        """
        distancia_total = distancia_km * 2 if ida_e_volta else distancia_km

        # Custo do combustível/transporte
        custo_transporte = distancia_total * self.custo_por_km

        # Custo do tempo (se habilitado)
        custo_tempo = 0.0
        tempo_horas = 0.0

        if self.considerar_tempo:
            tempo_horas = distancia_total / self.VELOCIDADE_MEDIA_URBANA
            custo_tempo = tempo_horas * self.VALOR_TEMPO_HORA

        custo_total = custo_transporte + custo_tempo

        return {
            "distancia_km": distancia_km,
            "distancia_total_km": distancia_total,
            "custo_transporte": round(custo_transporte, 2),
            "custo_tempo": round(custo_tempo, 2),
            "tempo_estimado_minutos": round(tempo_horas * 60, 0),
            "custo_total": round(custo_total, 2)
        }

    def analisar_economia(
        self,
        preco_mais_proximo: float,
        preco_mais_barato: float,
        distancia_mais_proximo_km: float,
        distancia_mais_barato_km: float
    ) -> Dict:
        """
        Analisa se vale a pena ir ao lugar mais barato

        Args:
            preco_mais_proximo: Preço no supermercado mais próximo
            preco_mais_barato: Preço no supermercado mais barato
            distancia_mais_proximo_km: Distância até o mais próximo
            distancia_mais_barato_km: Distância até o mais barato

        Returns:
            Dicionário com análise completa
        """
        # Economia no produto
        economia_produto = preco_mais_proximo - preco_mais_barato
        economia_percentual = ((economia_produto / preco_mais_proximo) * 100) if preco_mais_proximo > 0 else 0

        # Custo de ir ao mais próximo
        custo_proximo = self.calcular_custo_deslocamento(distancia_mais_proximo_km)

        # Custo de ir ao mais barato
        custo_barato = self.calcular_custo_deslocamento(distancia_mais_barato_km)

        # Custo adicional de ir ao mais barato
        custo_adicional = custo_barato["custo_total"] - custo_proximo["custo_total"]

        # Economia líquida (economia no produto - custo adicional do deslocamento)
        economia_liquida = economia_produto - custo_adicional

        # Vale a pena?
        vale_a_pena = economia_liquida > 0

        return {
            "vale_a_pena": vale_a_pena,
            "economia_produto": round(economia_produto, 2),
            "economia_percentual": round(economia_percentual, 1),
            "custo_adicional_deslocamento": round(custo_adicional, 2),
            "economia_liquida": round(economia_liquida, 2),
            "local_proximo": {
                "distancia_km": distancia_mais_proximo_km,
                "preco": preco_mais_proximo,
                "custo_deslocamento": custo_proximo
            },
            "local_barato": {
                "distancia_km": distancia_mais_barato_km,
                "preco": preco_mais_barato,
                "custo_deslocamento": custo_barato
            },
            "recomendacao": self._gerar_recomendacao(
                vale_a_pena,
                economia_liquida,
                economia_percentual,
                custo_barato["tempo_estimado_minutos"] - custo_proximo["tempo_estimado_minutos"]
            )
        }

    def _gerar_recomendacao(
        self,
        vale_a_pena: bool,
        economia_liquida: float,
        economia_percentual: float,
        tempo_adicional_minutos: float
    ) -> str:
        """Gera recomendação textual"""
        if not vale_a_pena:
            return (f"Não vale a pena. Você gastaria R$ {abs(economia_liquida):.2f} a mais "
                   f"indo ao lugar mais barato (considerando deslocamento).")

        if economia_liquida < 2:
            return (f"Vale pouco a pena. Economia de apenas R$ {economia_liquida:.2f} "
                   f"para {tempo_adicional_minutos:.0f} minutos a mais de viagem.")

        if economia_liquida < 5:
            return (f"Vale razoavelmente a pena. Você economiza R$ {economia_liquida:.2f} "
                   f"({economia_percentual:.1f}%), mas são {tempo_adicional_minutos:.0f} minutos a mais.")

        return (f"Vale muito a pena! Você economiza R$ {economia_liquida:.2f} "
               f"({economia_percentual:.1f}%) indo ao lugar mais barato.")


def ranquear_precos_por_custo_beneficio(
    precos_com_localizacao: List[Dict],
    lat_usuario: float,
    lon_usuario: float,
    tipo_transporte: str = "carro",
    considerar_tempo: bool = True
) -> List[Dict]:
    """
    Ranqueia preços considerando distância e custo-benefício

    Args:
        precos_com_localizacao: Lista de dicts com {preco, supermercado, latitude, longitude}
        lat_usuario: Latitude do usuário
        lon_usuario: Longitude do usuário
        tipo_transporte: Tipo de transporte ("carro", "moto", "onibus")
        considerar_tempo: Se deve considerar o valor do tempo

    Returns:
        Lista ordenada por melhor custo-benefício (preço + deslocamento)
    """
    geo = GeoLocalizacao()
    analisador = AnalisadorCustoBeneficio(tipo_transporte, considerar_tempo)

    resultados = []

    for item in precos_com_localizacao:
        # Calcula distância
        distancia = geo.calcular_distancia(
            lat_usuario,
            lon_usuario,
            item["latitude"],
            item["longitude"]
        )

        # Calcula custo do deslocamento
        custo_deslocamento = analisador.calcular_custo_deslocamento(distancia)

        # Custo total = preço do produto + custo do deslocamento
        custo_total = item["preco"] + custo_deslocamento["custo_total"]

        resultados.append({
            **item,
            "distancia_km": round(distancia, 2),
            "custo_deslocamento": custo_deslocamento,
            "custo_total_real": round(custo_total, 2),
            "tempo_estimado_minutos": custo_deslocamento["tempo_estimado_minutos"]
        })

    # Ordena por custo total real (preço + deslocamento)
    resultados.sort(key=lambda x: x["custo_total_real"])

    # Adiciona posição no ranking
    for idx, item in enumerate(resultados):
        item["ranking"] = idx + 1
        item["melhor_opcao"] = idx == 0

    return resultados
