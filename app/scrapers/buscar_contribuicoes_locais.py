"""
Busca contribuicoes de precos feitas por usuarios proximos a localizacao
Prioriza dados reais da comunidade antes de buscar na internet
"""
from typing import List, Dict, Optional
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta


def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distancia entre dois pontos GPS usando formula de Haversine
    Retorna distancia em km
    """
    R = 6371.0  # Raio da Terra em km

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def buscar_contribuicoes_locais(
    db: Session,
    termo: str,
    latitude: float,
    longitude: float,
    raio_km: float = 15.0,
    limite: int = 50,
    dias_max: int = 30
) -> List[Dict]:
    """
    Busca precos contribuidos por usuarios proximos a localizacao

    Args:
        db: Sessao do banco de dados
        termo: Termo de busca (ex: "arroz", "cafe")
        latitude: Latitude do usuario
        longitude: Longitude do usuario
        raio_km: Raio de busca em km (padrao: 15km)
        limite: Limite de resultados
        dias_max: Considerar contribuicoes dos ultimos X dias

    Returns:
        Lista de produtos com preco, distancia e informacoes do supermercado
    """
    from app.models.database import Preco, Produto

    print(f"\n[CONTRIB LOCAL] Buscando contribuicoes proximas a ({latitude}, {longitude})")
    print(f"   Termo: '{termo}' | Raio: {raio_km}km | Dias: {dias_max}")

    # Data minima para considerar
    data_minima = datetime.now() - timedelta(days=dias_max)

    # Buscar precos que tenham geolocalizacao e correspondam ao termo
    # Primeiro, buscar todos os precos com lat/lon e filtrar em Python
    # (SQLite nao tem funcoes geograficas nativas)

    query = db.query(Preco, Produto).join(Produto).filter(
        and_(
            Preco.latitude.isnot(None),
            Preco.longitude.isnot(None),
            Preco.data_coleta >= data_minima,
            or_(
                Produto.nome.ilike(f"%{termo}%"),
                Produto.marca.ilike(f"%{termo}%"),
                Produto.categoria.ilike(f"%{termo}%")
            )
        )
    ).order_by(Preco.data_coleta.desc())

    resultados_db = query.all()

    print(f"   Encontrados {len(resultados_db)} precos com geolocalizacao no banco")

    # Filtrar por distancia e calcular
    contribuicoes = []

    for preco, produto in resultados_db:
        distancia = calcular_distancia_km(
            latitude, longitude,
            preco.latitude, preco.longitude
        )

        # Filtrar pelo raio
        if distancia <= raio_km:
            # Calcular "frescor" do preco (mais recente = melhor)
            dias_desde_coleta = (datetime.now() - preco.data_coleta).days
            frescor = max(0, 100 - (dias_desde_coleta * 3))  # -3 pontos por dia

            contribuicoes.append({
                'nome': produto.nome,
                'marca': produto.marca,
                'preco': preco.preco,
                'preco_original': preco.preco_original,
                'em_promocao': preco.em_promocao,
                'supermercado': preco.supermercado,
                'latitude': preco.latitude,
                'longitude': preco.longitude,
                'endereco': preco.endereco or preco.localizacao,
                'distancia_km': round(distancia, 2),
                'data_coleta': preco.data_coleta.isoformat() if preco.data_coleta else None,
                'usuario_nome': preco.usuario_nome,
                'verificado': preco.verificado,
                'foto_url': preco.foto_url,
                'fonte': 'contribuicao_local',
                'produto_real': True,
                'frescor': frescor,
                'dias_atras': dias_desde_coleta
            })

    # Ordenar por distancia (mais proximo primeiro)
    contribuicoes.sort(key=lambda x: (x['distancia_km'], -x['frescor']))

    # Limitar resultados
    contribuicoes = contribuicoes[:limite]

    print(f"   [OK] {len(contribuicoes)} contribuicoes dentro de {raio_km}km")

    if contribuicoes:
        print(f"\n   Contribuicoes mais proximas:")
        for i, c in enumerate(contribuicoes[:5], 1):
            print(f"   {i}. {c['nome']} - R${c['preco']:.2f}")
            print(f"      {c['supermercado']} ({c['distancia_km']}km) - {c['dias_atras']} dias atras")

    return contribuicoes


def buscar_contribuicoes_por_supermercado(
    db: Session,
    termo: str,
    supermercado: str,
    limite: int = 20
) -> List[Dict]:
    """
    Busca contribuicoes de um supermercado especifico
    """
    from app.models.database import Preco, Produto

    query = db.query(Preco, Produto).join(Produto).filter(
        and_(
            Preco.supermercado.ilike(f"%{supermercado}%"),
            or_(
                Produto.nome.ilike(f"%{termo}%"),
                Produto.marca.ilike(f"%{termo}%")
            )
        )
    ).order_by(Preco.data_coleta.desc()).limit(limite)

    resultados = []
    for preco, produto in query.all():
        resultados.append({
            'nome': produto.nome,
            'marca': produto.marca,
            'preco': preco.preco,
            'supermercado': preco.supermercado,
            'latitude': preco.latitude,
            'longitude': preco.longitude,
            'endereco': preco.endereco or preco.localizacao,
            'data_coleta': preco.data_coleta.isoformat() if preco.data_coleta else None,
            'fonte': 'contribuicao',
            'produto_real': True
        })

    return resultados


def contar_contribuicoes_regiao(
    db: Session,
    latitude: float,
    longitude: float,
    raio_km: float = 10.0
) -> Dict:
    """
    Conta estatisticas de contribuicoes em uma regiao
    """
    from app.models.database import Preco

    # Buscar todos os precos com geolocalizacao
    precos = db.query(Preco).filter(
        and_(
            Preco.latitude.isnot(None),
            Preco.longitude.isnot(None)
        )
    ).all()

    total_na_regiao = 0
    supermercados = set()

    for preco in precos:
        distancia = calcular_distancia_km(
            latitude, longitude,
            preco.latitude, preco.longitude
        )
        if distancia <= raio_km:
            total_na_regiao += 1
            supermercados.add(preco.supermercado)

    return {
        'total_contribuicoes': total_na_regiao,
        'total_supermercados': len(supermercados),
        'supermercados': list(supermercados),
        'raio_km': raio_km
    }
