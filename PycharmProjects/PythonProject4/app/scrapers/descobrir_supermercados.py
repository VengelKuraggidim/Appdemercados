"""
Descobre supermercados próximos usando geolocalização
Usa APIs públicas para encontrar supermercados reais na região do usuário
"""
from typing import List, Dict, Optional
import requests
import json


class DescobrirSupermercados:
    """
    Descobre supermercados próximos à localização do usuário
    """

    def __init__(self):
        # Usar API gratuita do OpenStreetMap (Overpass API)
        self.overpass_url = "https://overpass-api.de/api/interpreter"

        # Nominatim para geocoding reverso (descobrir endereço)
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"

    def descobrir_por_gps(
        self,
        latitude: float,
        longitude: float,
        raio_km: float = 5.0
    ) -> List[Dict]:
        """
        Descobre supermercados reais próximos às coordenadas GPS

        Args:
            latitude: Latitude do usuário
            longitude: Longitude do usuário
            raio_km: Raio de busca em km (padrão: 5km)

        Returns:
            Lista de supermercados com nome, endereço, distância, coordenadas
        """
        print(f"\n🔍 Descobrindo supermercados próximos a ({latitude}, {longitude})")
        print(f"   📏 Raio de busca: {raio_km} km")

        # Converter raio de km para metros
        raio_metros = raio_km * 1000

        # Query Overpass para buscar supermercados
        # Busca por tag "shop=supermarket" no OpenStreetMap
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["shop"="supermarket"](around:{raio_metros},{latitude},{longitude});
          way["shop"="supermarket"](around:{raio_metros},{latitude},{longitude});
          relation["shop"="supermarket"](around:{raio_metros},{latitude},{longitude});
        );
        out center;
        """

        supermercados = []

        try:
            response = requests.post(
                self.overpass_url,
                data={'data': overpass_query},
                timeout=30,
                headers={'User-Agent': 'AppDeMercados/1.0'}
            )

            if response.status_code != 200:
                print(f"   ❌ Erro na API Overpass: {response.status_code}")
                return []

            data = response.json()
            elementos = data.get('elements', [])

            print(f"   ✅ Encontrados {len(elementos)} supermercados no OpenStreetMap")

            for elemento in elementos:
                try:
                    # Pegar coordenadas (node tem lat/lon direto, way/relation tem center)
                    if elemento['type'] == 'node':
                        lat = elemento['lat']
                        lon = elemento['lon']
                    else:
                        # Way ou relation tem center
                        lat = elemento.get('center', {}).get('lat')
                        lon = elemento.get('center', {}).get('lon')

                    if not lat or not lon:
                        continue

                    # Pegar tags (nome, endereço, etc.)
                    tags = elemento.get('tags', {})

                    nome = tags.get('name', 'Supermercado')
                    brand = tags.get('brand', '')  # Marca/rede

                    # Montar nome completo
                    nome_completo = brand if brand else nome

                    # Endereço
                    rua = tags.get('addr:street', '')
                    numero = tags.get('addr:housenumber', '')
                    bairro = tags.get('addr:suburb', '')
                    cidade = tags.get('addr:city', '')

                    endereco_parts = []
                    if rua:
                        endereco_parts.append(rua)
                    if numero:
                        endereco_parts.append(numero)
                    if bairro:
                        endereco_parts.append(bairro)
                    if cidade:
                        endereco_parts.append(cidade)

                    endereco = ', '.join(endereco_parts) if endereco_parts else None

                    # Calcular distância aproximada
                    distancia_km = self._calcular_distancia(
                        latitude, longitude, lat, lon
                    )

                    # Telefone, website
                    telefone = tags.get('phone', tags.get('contact:phone'))
                    website = tags.get('website', tags.get('contact:website'))

                    supermercados.append({
                        'nome': nome_completo,
                        'brand': brand if brand else None,
                        'endereco': endereco,
                        'latitude': lat,
                        'longitude': lon,
                        'distancia_km': round(distancia_km, 2),
                        'telefone': telefone,
                        'website': website,
                        'fonte': 'openstreetmap'
                    })

                except Exception as e:
                    continue

            # Ordenar por distância
            supermercados.sort(key=lambda x: x['distancia_km'])

            print(f"   📍 Processados {len(supermercados)} supermercados com dados completos")

            # Mostrar preview
            if supermercados:
                print(f"\n   🏪 Supermercados mais próximos:")
                for i, s in enumerate(supermercados[:5], 1):
                    print(f"   {i}. {s['nome']} - {s['distancia_km']} km")
                    if s['endereco']:
                        print(f"      📍 {s['endereco']}")

        except Exception as e:
            print(f"   ❌ Erro ao buscar supermercados: {e}")

        return supermercados

    def descobrir_por_endereco(self, endereco: str) -> List[Dict]:
        """
        Descobre supermercados próximos a um endereço

        Args:
            endereco: Endereço (ex: "Av. Paulista, 1000, São Paulo")

        Returns:
            Lista de supermercados
        """
        print(f"\n🔍 Buscando localização de: {endereco}")

        # Primeiro, geocode o endereço para pegar lat/lon
        try:
            geocode_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': endereco,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }

            response = requests.get(
                geocode_url,
                params=params,
                headers={'User-Agent': 'AppDeMercados/1.0'},
                timeout=10
            )

            if response.status_code != 200 or not response.json():
                print(f"   ❌ Não foi possível geocodificar o endereço")
                return []

            result = response.json()[0]
            latitude = float(result['lat'])
            longitude = float(result['lon'])

            print(f"   ✅ Localização encontrada: ({latitude}, {longitude})")

            # Agora buscar supermercados próximos
            return self.descobrir_por_gps(latitude, longitude)

        except Exception as e:
            print(f"   ❌ Erro no geocoding: {e}")
            return []

    def descobrir_cidade(self, latitude: float, longitude: float) -> str:
        """
        Descobre nome da cidade pelas coordenadas
        """
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json'
            }

            response = requests.get(
                self.nominatim_url,
                params=params,
                headers={'User-Agent': 'AppDeMercados/1.0'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})

                cidade = (
                    address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    address.get('municipality') or
                    'Desconhecida'
                )

                estado = address.get('state', '')

                return f"{cidade}, {estado}" if estado else cidade

        except Exception:
            pass

        return "Desconhecida"

    def _calcular_distancia(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calcula distância entre dois pontos GPS (fórmula de Haversine)
        Retorna distância em km
        """
        from math import radians, sin, cos, sqrt, atan2

        # Raio da Terra em km
        R = 6371.0

        # Converter para radianos
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        # Diferenças
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Fórmula de Haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distancia = R * c

        return distancia


# Instância global
descobrir_supermercados = DescobrirSupermercados()


# Função de teste
def testar_descoberta(latitude: float = None, longitude: float = None):
    """
    Testa a descoberta de supermercados

    Uso:
        testar_descoberta(-23.5505, -46.6333)  # Av. Paulista, SP
    """
    if latitude is None or longitude is None:
        # Padrão: Av. Paulista, São Paulo
        latitude = -23.5505
        longitude = -46.6333
        print("⚠️  Usando coordenadas padrão (Av. Paulista, SP)")

    descobridor = DescobrirSupermercados()

    # Descobrir cidade
    cidade = descobridor.descobrir_cidade(latitude, longitude)
    print(f"\n📍 Cidade detectada: {cidade}")

    # Descobrir supermercados
    supermercados = descobridor.descobrir_por_gps(latitude, longitude, raio_km=5.0)

    print(f"\n{'='*70}")
    print(f"✅ Total: {len(supermercados)} supermercados encontrados")
    print(f"{'='*70}")

    return supermercados
