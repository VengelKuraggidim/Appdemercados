# Guia de Geolocalização e Análise de Custo-Benefício

## 📍 Visão Geral

O sistema agora inclui análise inteligente de custo-benefício que considera:
- **Distância** até cada supermercado
- **Custo do deslocamento** (combustível/transporte)
- **Tempo estimado** de viagem
- **Economia real** após descontar custos de deslocamento

## 🚀 Como Usar

### 1. Frontend - Busca Otimizada

Quando o usuário permite acesso à localização, aparece um checkbox:
```
📍 Buscar considerando distância e custo de deslocamento
```

Com essa opção ativada, a busca mostra:
- Distância em km até cada supermercado
- Tempo estimado de viagem
- Custo de ida e volta
- **Custo total real** (preço do produto + deslocamento)

### 2. API Endpoints

#### `/api/buscar-otimizado` (POST)
Busca produtos ordenados por melhor custo-benefício real.

**Parâmetros:**
- `termo`: Produto a buscar
- `latitude`: Localização do usuário
- `longitude`: Localização do usuário
- `tipo_transporte`: "carro", "moto", "onibus" (padrão: "carro")
- `considerar_tempo`: true/false (padrão: true)

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/api/buscar-otimizado?termo=arroz&latitude=-23.5505&longitude=-46.6333&tipo_transporte=carro"
```

**Resposta:**
```json
{
  "termo": "arroz",
  "total": 5,
  "usuario": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "tipo_transporte": "carro"
  },
  "produtos": [
    {
      "nome": "Arroz Tio João 5kg",
      "preco": 18.90,
      "supermercado": "Atacadão",
      "distancia_km": 2.5,
      "custo_deslocamento": {
        "custo_transporte": 4.00,
        "custo_tempo": 2.50,
        "custo_total": 6.50,
        "tempo_estimado_minutos": 10
      },
      "custo_total_real": 25.40,
      "ranking": 1,
      "melhor_opcao": true
    }
  ]
}
```

#### `/api/analisar-economia` (GET)
Analisa se vale a pena ir ao supermercado mais barato vs. mais próximo.

**Parâmetros:**
- `produto_id`: ID do produto
- `latitude_usuario`: Localização do usuário
- `longitude_usuario`: Localização do usuário
- `tipo_transporte`: "carro", "moto", "onibus"
- `considerar_tempo`: true/false

**Exemplo:**
```bash
curl "http://localhost:8000/api/analisar-economia?produto_id=1&latitude_usuario=-23.5505&longitude_usuario=-46.6333&tipo_transporte=carro"
```

**Resposta:**
```json
{
  "produto": "Arroz Tio João 5kg",
  "analise": {
    "vale_a_pena": true,
    "economia_produto": 3.50,
    "economia_percentual": 15.6,
    "custo_adicional_deslocamento": 2.00,
    "economia_liquida": 1.50,
    "local_proximo": {
      "supermercado": "Carrefour",
      "preco": 22.40,
      "distancia_km": 1.0,
      "endereco": "Av. Paulista, 1000"
    },
    "local_barato": {
      "supermercado": "Atacadão",
      "preco": 18.90,
      "distancia_km": 2.5,
      "endereco": "R. da Consolação, 500"
    },
    "recomendacao": "Vale muito a pena! Você economiza R$ 1.50 (15.6%) indo ao lugar mais barato."
  }
}
```

#### `/api/calcular-distancia` (GET)
Calcula distância entre dois pontos.

**Parâmetros:**
- `lat1`, `lon1`: Primeiro ponto
- `lat2`, `lon2`: Segundo ponto

## 💰 Custos Configurados

### Por tipo de transporte:
- **Carro**: R$ 0,80/km (combustível + desgaste)
- **Moto**: R$ 0,35/km
- **Ônibus**: R$ 0,25/km

### Valor do tempo:
- R$ 15,00/hora (baseado em salário mínimo)
- Velocidade média urbana: 30 km/h

## 🔧 Implementação Backend

### 1. Adicionar Geolocalização ao Contribuir

Quando o usuário contribui com um preço, agora pode enviar coordenadas:

```python
@app.post("/api/contribuir")
async def adicionar_preco_manual(
    contribuicao: PrecoManualCreate,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    endereco: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # ... cria produto ...

    novo_preco = Preco(
        # ... outros campos ...
        latitude=latitude,
        longitude=longitude,
        endereco=endereco
    )
```

### 2. Módulo de Geolocalização

O módulo `app/utils/geolocalizacao.py` contém:

**Classes principais:**
- `GeoLocalizacao`: Cálculo de distâncias (Haversine)
- `AnalisadorCustoBeneficio`: Análise de economia vs. custo
- `ranquear_precos_por_custo_beneficio()`: Ordenação inteligente

**Exemplo de uso:**
```python
from app.utils.geolocalizacao import GeoLocalizacao, AnalisadorCustoBeneficio

# Calcular distância
geo = GeoLocalizacao()
distancia = geo.calcular_distancia(-23.5505, -46.6333, -23.5489, -46.6388)
# distancia = 0.85 km

# Analisar economia
analisador = AnalisadorCustoBeneficio(tipo_transporte="carro")
analise = analisador.analisar_economia(
    preco_mais_proximo=22.40,
    preco_mais_barato=18.90,
    distancia_mais_proximo_km=1.0,
    distancia_mais_barato_km=2.5
)
print(analise["vale_a_pena"])  # True ou False
print(analise["economia_liquida"])  # R$ 1.50
```

## 📱 Frontend JavaScript

### Obter Localização do Usuário

```javascript
function requestUserLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
            }
        );
    }
}
```

### Buscar com Geolocalização

```javascript
async function buscarProdutos() {
    if (userLocation && useGeoOptimization) {
        const response = await fetch(
            `${API_URL}/api/buscar-otimizado?` +
            `termo=${termo}&` +
            `latitude=${userLocation.latitude}&` +
            `longitude=${userLocation.longitude}&` +
            `tipo_transporte=carro`
        );
    }
}
```

## 🗄️ Banco de Dados

### Alterações na tabela `precos`:

```sql
ALTER TABLE precos ADD COLUMN latitude REAL;
ALTER TABLE precos ADD COLUMN longitude REAL;
ALTER TABLE precos ADD COLUMN endereco TEXT;
```

Ou rode novamente `init_db()` para recriar as tabelas.

## 🧪 Testando

### 1. Popular dados com geolocalização:

```python
# Exemplo: Adicionar preços com coordenadas
novo_preco = Preco(
    produto_id=1,
    supermercado="Carrefour",
    preco=22.40,
    latitude=-23.5505,  # Av. Paulista
    longitude=-46.6333,
    endereco="Av. Paulista, 1000 - São Paulo"
)
```

### 2. Testar endpoint de análise:

```bash
# Buscar produtos com geolocalização
curl -X POST "http://localhost:8000/api/buscar-otimizado?termo=arroz&latitude=-23.5505&longitude=-46.6333"

# Analisar economia
curl "http://localhost:8000/api/analisar-economia?produto_id=1&latitude_usuario=-23.5505&longitude_usuario=-46.6333"
```

## 🎯 Próximos Passos

1. **Adicionar mais tipos de transporte** (bicicleta, a pé)
2. **Personalização de custos** pelo usuário
3. **Rota múltipla** (comprar em vários supermercados)
4. **Histórico de rotas** mais econômicas
5. **Mapa visual** dos supermercados

## ⚠️ Notas Importantes

- A geolocalização é **opcional** - o app funciona sem ela
- Sempre peça permissão do usuário para acessar localização
- Coordenadas precisam ser cadastradas manualmente nas contribuições
- Para produção, considere usar API de geocoding (converter endereço → coordenadas)
