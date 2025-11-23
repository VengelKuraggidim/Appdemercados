# 📦 Sistema de Produtos - Como Funciona

## 🎯 Filosofia

O app **SEMPRE prioriza produtos REAIS** adicionados pelos usuários.

Produtos gerados (fake) **NUNCA devem aparecer** se houver produtos reais disponíveis.

## 🔄 Fluxo de Busca

### 1. Usuário busca "café"

```
┌─────────────────────────────────────┐
│  Usuário busca "café"               │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  1. Buscar no BANCO DE DADOS        │
│     - Produtos que usuários         │
│       adicionaram manualmente       │
│     - Ordenados por DATA            │
│       (mais recentes primeiro!)     │
│     - Últimos 30 dias               │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  Encontrou produtos?                │
└────────┬──────────┬─────────────────┘
         │ SIM      │ NÃO
         ▼          ▼
    ┌────────┐  ┌──────────────────┐
    │ Retorna│  │ AVISO: Sem       │
    │produtos│  │ produtos reais!  │
    │ REAIS  │  │ Incentive        │
    │        │  │ contribuição     │
    └────────┘  └──────────────────┘
```

## ✅ Produtos REAIS (Prioridade)

### Fontes de produtos reais:

1. **Contribuição manual** (usuários adicionam)
   - Usuário tira foto da nota fiscal
   - Ou digita preço manualmente
   - **Marcado como**: `fonte: 'contribuicao'`, `produto_real: true`

2. **Scraping REAL** (desativado por padrão - muito lento)
   - Scraping de sites reais (Mercado Livre, etc.)
   - Demora 15-30 segundos
   - Taxa de sucesso: ~60%
   - **Marcado como**: `fonte: 'scraper_tempo_real'`, `produto_real: true`

### Ordenação

Produtos REAIS são ordenados por:
```sql
ORDER BY data_coleta DESC  -- Mais recentes primeiro!
```

## ❌ Produtos GERADOS (Fallback - EVITAR!)

### Quando usar:

**APENAS** quando:
- Não há produtos reais no banco
- Scraping falhou
- E usuário precisa ver algum resultado

### Como identificar:

```javascript
produto.fonte === 'gerador_sob_demanda'  // É fake!
produto.produto_real === false            // Não é real!
```

### Avisar usuário:

```
⚠️ Produtos simulados (não há dados reais ainda)
💡 Adicione preços para ver produtos reais!
```

## 📍 Geolocalização

### Quando usuário marca "buscar considerando distância":

1. **Busca produtos reais do banco COM GPS**
2. **Calcula distância** de cada produto
3. **Filtra**: apenas produtos ≤5km
4. **Ordena**: mais próximos primeiro

### Problema atual:

Muitos produtos no banco **NÃO têm GPS** (contribuições antigas).

**Solução**:
- Incentivar usuários a permitir GPS ao adicionar preços
- Mostrar aviso quando produto não tem GPS
- Não mostrar análise de custo-benefício sem GPS

## 🎨 Interface

### Badge de produto REAL:

```
✅ Preço real (adicionado há 2 horas)
🕐 Atualizado: Hoje, 14:30
👤 Por: João123
```

### Badge de produto GERADO:

```
⚠️ Preço estimado (sem dados reais)
💡 Seja o primeiro a adicionar o preço real!
```

## 🔧 Como Desativar Gerador

### No scraper_tempo_real.py:

```python
def buscar_todos(
    termo: str,
    usar_scraper_real: bool = False,   # Scraping REAL (lento)
    usar_gerador_fallback: bool = False  # DESATIVA gerador fake!
):
    # Se NÃO encontrar produtos reais E gerador desativado:
    return []  # Retorna vazio
```

### No main.py:

```python
produtos = scraper_tempo_real.buscar_todos(
    termo,
    usar_scraper_real=False,      # Não scraping
    usar_gerador_fallback=False   # Não gerador fake
)

if not produtos:
    return {
        "message": "Nenhum produto real encontrado. Adicione preços!",
        "produtos": []
    }
```

## 📊 Status Atual

### Banco de Dados:
- Poucos produtos (app novo)
- Alguns sem GPS (contribuições antigas)
- Precisa crescer com contribuições

### Scraper:
- Gerador: ✅ Ativo (fallback)
- Scraping Real: ❌ Desativado (muito lento)

### Recomendação:

1. **Desativar gerador** quando tiver produtos suficientes
2. **Incentivar contribuições** (gamificação, tokens)
3. **Mostrar claramente** quando é produto fake
4. **Priorizar sempre** produtos reais

## 🚀 Roadmap

### Fase 1 (Atual):
- ✅ Produtos do banco (reais)
- ✅ Ordenados por data
- ⚠️ Gerador como fallback

### Fase 2 (Próximo):
- [ ] Desativar gerador
- [ ] Badge claro "REAL" vs "ESTIMADO"
- [ ] Incentivo a contribuir

### Fase 3 (Futuro):
- [ ] Scraping real seletivo (ativado por usuário)
- [ ] Cache de produtos reais
- [ ] API de supermercados parceiros
