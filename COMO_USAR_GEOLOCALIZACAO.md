# 📍 Como Usar a Análise de Custo-Benefício por Geolocalização

## ✅ Passo a Passo Rápido

### 1. Acesse o App
```
http://localhost:8000
```
ou
```
http://localhost:8080
```

### 2. Permita o Acesso à Localização
- O navegador vai pedir permissão
- **Clique em "Permitir"**

### 3. Ative a Busca Otimizada
- Após permitir localização, aparecerá um **checkbox verde**:
```
☑️ Buscar considerando distância e custo de deslocamento
```
- **Marque esse checkbox!**

### 4. Faça uma Busca
Digite qualquer um desses produtos (já estão no banco com geolocalização):
- arroz
- feijão
- óleo
- açúcar
- café
- macarrão

### 5. Veja a Análise!
Cada resultado mostrará um box verde com:

```
💰 Análise de Custo-Benefício [i]

📍 Distância: 2.5 km
⏱️ Tempo estimado: 10 min
🚗 Combustível/Transporte: R$ 4.00
⌚ Custo do tempo: R$ 2.50
━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Custo Real Total: R$ 25.40

✅ Melhor opção! Economia de R$ 3.50 vs. Carrefour
```

---

## 🚫 Problema: Não Vejo as Mudanças?

### Solução Rápida (em ordem):

1. **Hard Refresh**
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Limpar Cache do Navegador**
   - Chrome: `F12` → Botão direito no reload → "Limpar cache e fazer recarga forçada"

3. **Abrir no Modo Anônimo**
   - Chrome: `Ctrl + Shift + N`
   - Acessar: `http://localhost:8000`

4. **Verificar Console por Erros**
   - `F12` → aba Console
   - Procurar erros em vermelho

---

## 📊 O Que Está Acontecendo?

O sistema calcula:
1. **Distância** até cada supermercado (fórmula de Haversine)
2. **Custo do combustível** (R$ 0,80/km para carro, ida e volta)
3. **Custo do tempo** (baseado em R$ 15/hora)
4. **Custo total REAL** = Preço do produto + custos de deslocamento

E então **ordena os resultados** pelo melhor custo-benefício!

---

## 🧪 Dados de Teste

O banco tem 4 supermercados em São Paulo:

| Supermercado | Localização | Distância do Centro |
|-------------|-------------|---------------------|
| **Carrefour** | Av. Paulista | ~0 km (referência) |
| **Atacadão** | R. Consolação | ~0.6 km |
| **Pão de Açúcar** | R. Augusta | ~1.3 km |
| **Extra** | Av. Rebouças | ~2.2 km |

Sua localização de teste: **Av. Paulista, São Paulo**
- Lat: `-23.5505`
- Lon: `-46.6333`

---

## 🎯 Exemplo Real

**Buscar "arroz":**

Sem geolocalização:
1. Atacadão - R$ 18,90 (mais barato)
2. Carrefour - R$ 22,90
3. Extra - R$ 24,50
4. Pão de Açúcar - R$ 25,90

Com geolocalização (você está na Paulista):
1. **Carrefour** - R$ 24,50 total (R$ 22,90 + R$ 1,60 deslocamento) ✅ MELHOR!
2. Atacadão - R$ 24,70 total (R$ 18,90 + R$ 5,80 deslocamento)
3. Pão de Açúcar - R$ 29,30 total
4. Extra - R$ 32,60 total

**Resultado**: Mesmo sendo mais caro, vale mais a pena ir ao Carrefour pela proximidade!

---

## 💡 Dicas

- O ícone **[i]** ao lado do título tem tooltip explicativo
- Passe o mouse para ver detalhes
- A primeira opção é SEMPRE a melhor em custo-benefício
- Outros lugares mostram quanto você gastaria a mais

---

## 🐛 Troubleshooting

**"Nenhum produto encontrado com localização cadastrada"**
- Rode: `python popular_com_geolocalizacao.py`
- Isso recria o banco com dados de teste

**Checkbox de geolocalização não aparece**
- Seu navegador pode não suportar geolocalização
- Ou você negou permissão
- Recarregue e permita novamente

**Erros no console**
- Abra issue ou me avise
- Copie o erro completo

---

## 📞 Precisa de Ajuda?

1. Veja `ATUALIZAR_APP.md` para problemas de cache
2. Veja `GEOLOCATION_GUIDE.md` para detalhes técnicos da API
3. Rode `./start_app.sh` para reiniciar tudo
