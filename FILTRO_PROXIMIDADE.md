# 📍 Filtro de Proximidade - Busca por Distância

## 🎯 Visão Geral

Sistema inteligente de filtragem de produtos por **proximidade geográfica**, priorizando produtos mais próximos do usuário e limitando resultados dentro de um raio configurável.

## ✨ Melhorias Implementadas

### Antes
- ❌ Produtos de até 8km+ de distância apareciam nos resultados
- ❌ Sem controle sobre a distância máxima
- ⚠️ Produtos muito distantes misturados com próximos

### Agora
- ✅ **Distância máxima padrão: 5km**
- ✅ **Configurável** via parâmetro da API
- ✅ Produtos **ordenados** por proximidade (mais próximos primeiro)
- ✅ Produtos fora do raio são **excluídos** automaticamente
- ✅ Fallback para produtos sem localização apenas se necessário

## 🚀 Como Usar

### 1. Busca com Distância Padrão (5km)

```bash
curl -X POST "http://localhost:8000/api/buscar" \
  -H "Content-Type: application/json" \
  -d '{
    "termo": "arroz",
    "latitude": -23.5505,
    "longitude": -46.6333
  }'
```

**Resultado:** Apenas produtos até **5km** de distância

### 2. Busca com Distância Customizada

```bash
curl -X POST "http://localhost:8000/api/buscar" \
  -H "Content-Type: application/json" \
  -d '{
    "termo": "arroz",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "distancia_maxima_km": 3.0
  }'
```

**Resultado:** Apenas produtos até **3km** de distância

### 3. Busca Ampla (Raio Maior)

```bash
curl -X POST "http://localhost:8000/api/buscar" \
  -H "Content-Type: application/json" \
  -d '{
    "termo": "arroz",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "distancia_maxima_km": 10.0
  }'
```

**Resultado:** Produtos até **10km** de distância

## 📊 Resposta da API

```json
{
  "termo": "arroz",
  "total": 15,
  "ordenado_por_proximidade": true,
  "distancia_maxima_km": 5.0,
  "filtrado_por_distancia": true,
  "produtos": [
    {
      "nome": "Arroz Tio João 5kg",
      "preco": 25.90,
      "supermercado": "Carrefour",
      "latitude": -23.5501,
      "longitude": -46.6335,
      "distancia_km": 0.5,
      "endereco": "Av. Paulista, 1000"
    },
    {
      "nome": "Arroz Camil 5kg",
      "preco": 24.50,
      "supermercado": "Pão de Açúcar",
      "latitude": -23.5520,
      "longitude": -46.6340,
      "distancia_km": 1.8,
      "endereco": "R. Augusta, 500"
    }
  ]
}
```

## 🎯 Lógica de Filtragem

### Priorização

1. **Produtos com GPS dentro do raio** (0-5km)
   - Ordenados por distância crescente
   - Mostram distância em km

2. **Produtos sem GPS** (fallback)
   - Apenas se não houver produtos próximos
   - Limitados a 10 resultados
   - `distancia_km: null`

3. **Produtos fora do raio**
   - ❌ Não aparecem nos resultados

### Exemplo Prático

**Usuário em:** São Paulo (-23.5505, -46.6333)
**Distância máxima:** 5km

| Produto | Localização | Distância | Resultado |
|---------|-------------|-----------|-----------|
| Arroz A | Av. Paulista | 0.5km | ✅ Mostrado (1º) |
| Feijão B | R. Augusta | 1.8km | ✅ Mostrado (2º) |
| Café C | Pinheiros | 4.2km | ✅ Mostrado (3º) |
| Açúcar D | Santo André | 8.5km | ❌ Filtrado |
| Sal E | Sem GPS | - | ⚠️ Apenas se < 3 produtos |

## 📱 Integração Frontend

### JavaScript Example

```javascript
async function buscarProdutosProximos(termo, distanciaMaxKm = 5) {
  // Obter localização do usuário
  const position = await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject);
  });

  const { latitude, longitude } = position.coords;

  // Fazer busca com filtro de distância
  const response = await fetch('/api/buscar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      termo,
      latitude,
      longitude,
      distancia_maxima_km: distanciaMaxKm
    })
  });

  const data = await response.json();

  // Exibir produtos ordenados por proximidade
  data.produtos.forEach(produto => {
    console.log(`${produto.nome} - ${produto.distancia_km}km - R$ ${produto.preco}`);
  });
}

// Uso
buscarProdutosProximos('arroz', 5.0);  // Raio de 5km
buscarProdutosProximos('feijão', 3.0); // Raio de 3km
buscarProdutosProximos('café', 10.0);  // Raio de 10km
```

### React Example

```jsx
function BuscaProdutos() {
  const [produtos, setProdutos] = useState([]);
  const [distanciaMax, setDistanciaMax] = useState(5);

  const buscar = async (termo) => {
    const position = await getCurrentPosition();

    const response = await fetch('/api/buscar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        termo,
        latitude: position.latitude,
        longitude: position.longitude,
        distancia_maxima_km: distanciaMax
      })
    });

    const data = await response.json();
    setProdutos(data.produtos);
  };

  return (
    <div>
      <label>
        Raio máximo:
        <input
          type="range"
          min="1"
          max="20"
          value={distanciaMax}
          onChange={(e) => setDistanciaMax(e.target.value)}
        />
        {distanciaMax}km
      </label>

      {produtos.map(p => (
        <div key={p.id}>
          <h3>{p.nome}</h3>
          <p>R$ {p.preco}</p>
          <p>📍 {p.distancia_km}km - {p.endereco}</p>
        </div>
      ))}
    </div>
  );
}
```

## 🔧 Endpoints Atualizados

### `/api/buscar` (POST)

**Parâmetros:**
```typescript
{
  termo: string;                    // Termo de busca
  supermercados?: string[];         // Filtrar por mercados
  latitude?: number;                // Lat do usuário
  longitude?: number;               // Long do usuário
  distancia_maxima_km?: number;     // Raio máximo (padrão: 5km)
}
```

### `/api/promocoes/{supermercado}` (GET)

**Query Params:**
- `latitude`: Latitude do usuário
- `longitude`: Longitude do usuário
- `distancia_maxima_km`: Raio máximo (padrão: 5km)

**Exemplo:**
```
GET /api/promocoes/carrefour?latitude=-23.5505&longitude=-46.6333&distancia_maxima_km=3
```

## 📈 Benefícios

### Para o Usuário
- ✅ Resultados mais relevantes
- ✅ Economia de tempo (produtos próximos)
- ✅ Menos deslocamento
- ✅ Economia de combustível
- ✅ Controle sobre área de busca

### Para o Sistema
- ✅ Menos dados trafegados
- ✅ Respostas mais rápidas
- ✅ Melhor UX
- ✅ Maior precisão nos resultados
- ✅ Reduz frustração do usuário

## 💡 Casos de Uso

### 1. Busca Rápida (Raio Pequeno)
**Cenário:** Usuário a pé ou com pressa
**Configuração:** 1-2km
**Resultado:** Apenas produtos muito próximos

### 2. Busca Normal (Raio Médio)
**Cenário:** Usuário de carro, região urbana
**Configuração:** 5km (padrão)
**Resultado:** Bom equilíbrio quantidade/proximidade

### 3. Busca Ampla (Raio Grande)
**Cenário:** Região rural, produto raro
**Configuração:** 10-20km
**Resultado:** Mais opções, maior área

## ⚙️ Configurações Recomendadas

| Situação | Raio Sugerido |
|----------|--------------|
| 🚶 A pé | 1-2 km |
| 🚲 Bicicleta | 3-5 km |
| 🚗 Carro (cidade) | 5-7 km |
| 🚗 Carro (subúrbio) | 10-15 km |
| 🌾 Zona rural | 15-20 km |

## 🧪 Testes

### Teste 1: Filtro Funcionando
```python
import requests

response = requests.post('http://localhost:8000/api/buscar', json={
    'termo': 'arroz',
    'latitude': -23.5505,
    'longitude': -46.6333,
    'distancia_maxima_km': 3.0
})

produtos = response.json()['produtos']

# Verificar: todos produtos <= 3km
assert all(p['distancia_km'] <= 3.0 for p in produtos if p['distancia_km'])
print("✅ Filtro de distância funcionando!")
```

### Teste 2: Ordenação por Proximidade
```python
# Verificar ordem crescente
distancias = [p['distancia_km'] for p in produtos if p['distancia_km']]
assert distancias == sorted(distancias)
print("✅ Produtos ordenados por proximidade!")
```

## 📝 Notas Técnicas

### Cálculo de Distância

Utiliza a **fórmula de Haversine** para calcular distância entre coordenadas GPS:

```python
from app.utils.geolocalizacao import GeoLocalizacao

geo = GeoLocalizacao()
distancia = geo.calcular_distancia(
    lat1, lon1,  # Usuário
    lat2, lon2   # Produto
)
# Retorna distância em km
```

### Performance

- ✅ Cálculo rápido (< 1ms por produto)
- ✅ Filtro aplicado em memória
- ✅ Sem impacto no banco de dados
- ✅ Escalável para milhares de produtos

## 🔮 Melhorias Futuras

- [ ] Cache de distâncias calculadas
- [ ] Busca por polígono (não apenas raio)
- [ ] Considerar trânsito em tempo real
- [ ] Sugestão automática de raio ideal
- [ ] Heatmap de disponibilidade
- [ ] Rotas otimizadas para múltiplos produtos

---

**Versão:** 1.0.0
**Data:** 2025-10-31
**Status:** ✅ Implementado e Testado
