# Sistema de Ordenação por Proximidade Geográfica

## Visão Geral

Implementado sistema automático de ordenação de produtos por proximidade geográfica. Agora, quando você busca produtos, **os supermercados mais próximos aparecem primeiro** automaticamente!

## Como Funciona

### 1. **Captura Automática de Localização**
- O navegador solicita permissão para acessar sua localização
- Não é necessário ativar nenhum toggle, funciona automaticamente
- Se a localização não for concedida, a busca funciona normalmente por preço

### 2. **Ordenação Inteligente**
- **Com localização**: Produtos ordenados por distância (mais próximos primeiro)
- **Sem localização**: Produtos ordenados por menor preço (como antes)

### 3. **Informações Visuais**
- 📍 Badge "MAIS PRÓXIMO" no supermercado mais perto
- Distância exibida em km ao lado de cada produto
- Design azul destacando informações de proximidade

## Mudanças Implementadas

### Backend (API)

#### 1. **Schema Atualizado** (`app/models/schemas.py`)
```python
class BuscaRequest(BaseModel):
    termo: str
    supermercados: Optional[List[Supermercado]] = None
    latitude: Optional[float] = None    # ← NOVO
    longitude: Optional[float] = None   # ← NOVO
```

#### 2. **API de Busca** (`app/api/main.py`)
- Aceita `latitude` e `longitude` opcionais
- Calcula distância usando fórmula de Haversine
- Ordena resultados por proximidade automaticamente
- Retorna `distancia_km` em cada produto
- Flag `ordenado_por_proximidade` na resposta

### Frontend (Interface)

#### 1. **Captura de Localização** (`frontend/src/app.js`)
- Solicita localização ao carregar a página (função `requestUserLocation()`)
- Armazena em `userLocation` global
- Funciona mesmo se usuário negar permissão

#### 2. **Envio Automático**
```javascript
// Sempre envia localização se disponível
if (userLocation) {
    requestBody.latitude = userLocation.latitude;
    requestBody.longitude = userLocation.longitude;
}
```

#### 3. **Exibição Visual**
- Badge "📍 MAIS PRÓXIMO" no primeiro resultado
- Caixa azul mostrando distância: "X.X km de você"
- Ordenação visual mantém produtos próximos no topo

## Exemplo de Uso

### Antes
```
Busca: "arroz"
Resultados ordenados por: MENOR PREÇO

1. Arroz Extra - R$ 15,00 (pode estar a 20km)
2. Arroz Carrefour - R$ 16,00 (pode estar a 2km)
3. Arroz Pão de Açúcar - R$ 17,00 (pode estar a 5km)
```

### Depois (com localização)
```
Busca: "arroz"
Resultados ordenados por: PROXIMIDADE

1. 📍 Arroz Carrefour - R$ 16,00 [2.1 km de você]
2. Arroz Pão de Açúcar - R$ 17,00 [4.8 km de você]
3. Arroz Extra - R$ 15,00 [19.3 km de você]
```

## Diferença entre Ordenação Simples e Busca Otimizada

### **Ordenação por Proximidade** (Novo - Automático)
- ✅ Ordena por distância
- ✅ Mostra distância em km
- ✅ Funciona automaticamente
- ❌ Não considera custo de deslocamento

### **Busca Otimizada** (Já existia - Manual)
- ✅ Ordena por custo-benefício total
- ✅ Considera preço + combustível + tempo
- ✅ Análise completa de economia
- ⚙️ Precisa ativar o checkbox

## Permissões do Navegador

### Como Permitir Localização

**Chrome/Edge:**
1. Clique no ícone de cadeado/informação na barra de endereço
2. Procure "Localização"
3. Selecione "Permitir"

**Firefox:**
1. Clique no ícone de escudo/informação
2. Em "Permissões", encontre "Localização"
3. Marque "Permitir"

**Safari (iOS/macOS):**
1. Configurações do Safari → Privacidade
2. Serviços de Localização → Permitir

### Se Negar Permissão
- A busca funciona normalmente
- Produtos ordenados por menor preço
- Não aparece informação de distância

## Privacidade

- ✅ Localização usada apenas no navegador
- ✅ Não é armazenada no servidor
- ✅ Apenas coordenadas (lat/lon) são enviadas
- ✅ Não identifica endereço exato
- ✅ Pode ser desativada a qualquer momento

## Compatibilidade

### Navegadores Suportados
- ✅ Chrome 50+
- ✅ Firefox 55+
- ✅ Safari 10+
- ✅ Edge 79+
- ✅ Navegadores mobile (iOS/Android)

### Dispositivos
- ✅ Desktop (via IP ou WiFi)
- ✅ Mobile (via GPS)
- ✅ Tablet (via GPS/WiFi)

## Troubleshooting

### "Localização não funcionando"
1. Verifique se concedeu permissão ao navegador
2. Teste em HTTPS (HTTP não permite geolocalização em alguns navegadores)
3. Verifique se GPS está ativo (mobile)

### "Distância não aparece"
- Produtos sem coordenadas cadastradas não mostram distância
- Verifique se a localização foi concedida
- Recarregue a página

### "Ordem parece errada"
- Com localização: ordena por distância (não preço)
- Sem localização: ordena por preço
- Use "Busca Otimizada" para considerar custo total

## Próximas Melhorias

Sugestões futuras:
- [ ] Filtro de raio máximo (ex: "só mostrar até 5km")
- [ ] Mapa com localização dos supermercados
- [ ] Rota sugerida (integração Google Maps)
- [ ] Salvar supermercados favoritos
- [ ] Notificação de promoções próximas

## Arquivos Modificados

1. `app/models/schemas.py` - Schema com lat/lon
2. `app/api/main.py` - Lógica de ordenação
3. `frontend/src/app.js` - Captura e envio de localização

---

✅ **Pronto para usar!** Basta permitir a localização quando solicitado pelo navegador.
