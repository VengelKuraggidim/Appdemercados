# Sistema de Promoções por Supermercado

## Visão Geral

Implementado sistema completo para visualizar promoções de cada supermercado. Agora você pode **clicar duas vezes** em qualquer supermercado e ver todas as promoções disponíveis!

## 🔥 Como Usar

### **1. Visualizar Promoções**
1. Na barra de filtros de supermercados (acima da busca)
2. **Clique DUAS VEZES (duplo clique)** no supermercado desejado
3. Um modal aparecerá com todas as promoções

### **2. Ícone de Promoção**
- Todos os supermercados agora têm um ícone 🔥 ao lado
- Indica que você pode ver as promoções com duplo clique

### **3. Funcionalidades do Modal**
- 📊 Lista todas as promoções do supermercado
- 💰 Mostra preço original (riscado) e preço promocional
- 🏷️ Percentual de desconto em destaque
- 💵 Economia total em cada produto
- 📍 Distância de cada loja (se localização permitida)
- 🗂️ Ordenação inteligente:
  - **Com localização**: Ordenado por proximidade
  - **Sem localização**: Ordenado por maior desconto

## 🎯 Recursos Implementados

### Backend (API)

#### **Endpoint de Promoções**
```
GET /api/promocoes/{supermercado}
```

**Parâmetros opcionais:**
- `latitude` - Latitude do usuário
- `longitude` - Longitude do usuário

**Resposta:**
```json
{
  "supermercado": "Carrefour",
  "total": 15,
  "promocoes": [
    {
      "id": 123,
      "nome": "Arroz Tio João 5kg",
      "marca": "Tio João",
      "preco": 18.90,
      "preco_original": 24.90,
      "desconto_percentual": 24.1,
      "economia": 6.00,
      "distancia_km": 2.3,
      "endereco": "Av. Paulista, 1000"
    }
  ],
  "ordenado_por_proximidade": true
}
```

**Funcionalidades:**
- ✅ Busca apenas produtos em promoção (`em_promocao = True`)
- ✅ Filtra últimos 30 dias
- ✅ Calcula desconto percentual automaticamente
- ✅ Ordena por proximidade (com localização) ou desconto (sem localização)

### Frontend (Interface)

#### **Modal de Promoções**
- Design moderno com gradiente vermelho/laranja
- Cards com efeito hover (escala ao passar mouse)
- Preço original riscado
- Badge de desconto em destaque
- Informação de distância (se disponível)
- Botão X para fechar
- Clique fora do modal também fecha

#### **Interação nos Chips**
- **1 clique**: Filtra produtos (comportamento original)
- **2 cliques**: Abre modal de promoções (novo!)

## 📊 Exemplo de Promoção

```
╔══════════════════════════════════════════╗
║  🔥 Promoções Carrefour                 ║
╚══════════════════════════════════════════╝

📍 Ordenado por proximidade

┌──────────────────────────────────────────┐
│ Arroz Tio João 5kg                       │
│ Tio João                                 │
│ ̶R̶$̶ ̶2̶4̶.̶9̶0̶  R$ 18.90  [-24%]           │
│ 💰 Economia: R$ 6.00                     │
│ 📍 2.3 km de você                        │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ Feijão Camil 1kg                         │
│ Camil                                    │
│ ̶R̶$̶ ̶9̶.̶9̶0̶  R$ 6.90  [-30%]              │
│ 💰 Economia: R$ 3.00                     │
│ 📍 2.3 km de você                        │
└──────────────────────────────────────────┘

Total: 15 promoções encontradas
```

## 🔄 Fluxo de Uso

1. **Usuário abre a página**
   - Chips de supermercado carregam com ícone 🔥

2. **Usuário clica 2x no "Carrefour"**
   - Modal de "Carregando promoções..." aparece
   - API busca promoções do Carrefour
   - Se tem localização, envia lat/lon

3. **API processa**
   - Filtra promoções do Carrefour
   - Calcula descontos
   - Calcula distâncias (se localização fornecida)
   - Ordena resultados

4. **Modal atualiza**
   - Mostra todas as promoções
   - Destaca descontos
   - Mostra distâncias
   - Usuário pode fechar clicando X ou fora

## 💡 Dicas de Uso

### **Para ter mais promoções visíveis:**
1. Adicione produtos com `em_promocao: true` no banco
2. Preencha `preco_original` maior que `preco`
3. O sistema calculará o desconto automaticamente

### **Para ordenar por proximidade:**
1. Permita localização no navegador
2. As promoções mais próximas aparecerão primeiro

### **Exemplo de produto em promoção no banco:**
```python
preco = Preco(
    produto_id=1,
    supermercado="Carrefour",
    preco=18.90,
    preco_original=24.90,  # Preço antes da promoção
    em_promocao=True,      # Marca como promoção
    latitude=-23.550520,
    longitude=-46.633308
)
```

## 🎨 Visual

### **Chips de Supermercado**
```
┌──────────────┐  ┌────────────────┐  ┌──────────┐
│ Carrefour 🔥 │  │ Pão de Açúcar🔥│  │ Extra 🔥 │
└──────────────┘  └────────────────┘  └──────────┘
 (duplo clique)    (duplo clique)      (duplo clique)
```

### **Modal Design**
- **Header**: Gradiente vermelho/laranja com título
- **Body**: Cards de promoções intercalados (branco/cinza)
- **Footer**: Total de promoções encontradas
- **Animações**: FadeIn e SlideUp suaves

## 📱 Responsividade

- ✅ Desktop: Modal 800px largura máxima
- ✅ Mobile: Modal 90% da tela
- ✅ Scroll interno quando muitas promoções
- ✅ Altura máxima 80vh (evita overflow)

## 🔧 Arquivos Modificados

1. **`app/api/main.py`**
   - Novo endpoint `/api/promocoes/{supermercado}`
   - Lógica de cálculo de descontos
   - Ordenação por proximidade/desconto

2. **`frontend/src/app.js`**
   - Função `verPromocoesSupermercado()`
   - Função `criarModalPromocoes()`
   - Event listener de duplo clique nos chips
   - Ícone 🔥 adicionado aos chips

## 🚀 Próximas Melhorias

Sugestões futuras:
- [ ] Filtro de categoria dentro das promoções
- [ ] Comparar promoções entre supermercados
- [ ] Alertas de promoções próximas
- [ ] Histórico de promoções
- [ ] Compartilhar promoção via WhatsApp
- [ ] Notificação push de novas promoções

---

✅ **Pronto para usar!** Basta dar duplo clique em qualquer supermercado para ver as promoções! 🔥
