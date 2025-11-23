# 🎯 Sistema Híbrido Inteligente de OCR

## 🚀 O Que Foi Implementado?

Sistema de **3 níveis** que escolhe automaticamente o melhor OCR baseado em custo x precisão!

```
NÍVEL 1: EasyOCR (Grátis, Offline)
    ↓ Baixa confiança?
NÍVEL 2: Google Vision (1000/mês grátis) [Futuro]
    ↓ Nota muito complexa?
NÍVEL 3: Claude Vision (Pago, máxima precisão)
```

## 📊 Engines Disponíveis

| Engine | Custo | Precisão | Velocidade | Online/Offline |
|--------|-------|----------|------------|----------------|
| **EasyOCR** | 🟢 Grátis | ~70% | ~5s | ✅ Offline |
| **Google Vision** | 🟡 1000/mês grátis | ~90% | ~3s | ❌ Online |
| **Claude Vision** | 🔴 $0.04/nota | ~99% | ~8s | ❌ Online |

## 🔧 Como Usar

### Endpoint Principal: `/api/ocr-inteligente`

```bash
POST /api/ocr-inteligente
```

**Parâmetros**:
- `file`: Imagem da nota fiscal (obrigatório)
- `usuario_nome`: Nome do usuário para ganhar tokens (opcional)
- `modo`: Modo de processamento (opcional)
  - `"gratis"`: Só EasyOCR (100% grátis)
  - `"balanceado"`: EasyOCR → Google
  - `"premium"`: Tenta todos até encontrar melhor
  - `null`: Automático (recomendado)

### Exemplos de Uso

#### 1. Modo Grátis (EasyOCR)

```bash
curl -X POST http://localhost:8000/api/ocr-inteligente \
  -F "file=@nota_fiscal.jpg" \
  -F "usuario_nome=joao" \
  -F "modo=gratis"
```

**Características**:
- ✅ 100% grátis
- ✅ Funciona offline
- ⚠️ Precisão ~70%
- 🪙 Ganha 10 tokens por produto extraído

#### 2. Modo Automático (Inteligente)

```bash
curl -X POST http://localhost:8000/api/ocr-inteligente \
  -F "file=@nota_fiscal.jpg" \
  -F "usuario_nome=maria"
```

**Como funciona**:
1. Tenta EasyOCR primeiro (grátis)
2. Se confiança < 70% OU < 5 produtos → próximo nível
3. Retorna melhor resultado disponível

#### 3. Modo Premium (Máxima Precisão)

```bash
curl -X POST http://localhost:8000/api/ocr-inteligente \
  -F "file=@nota_fiscal.jpg" \
  -F "usuario_nome=carlos" \
  -F "modo=premium"
```

**Características**:
- Tenta todos os engines
- Máxima precisão possível
- Usa Claude se necessário
- 💰 Pode ter custo

### Resposta da API

```json
{
  "sucesso": true,
  "mensagem": "24 produtos adicionados!",
  "produtos_adicionados": 24,
  "produtos": [
    {
      "produto_id": 123,
      "nome": "File Peito Super Frango",
      "preco": 19.98,
      "supermercado": "Centro Oeste Comercial"
    }
    // ... mais produtos
  ],
  "tokens_ganhos": 240,
  "engine_usada": "EasyOCR",
  "confianca": 85.5,
  "dados_extraidos": {
    "supermercado": "Centro Oeste Comercial",
    "data_compra": "2025-10-02",
    "total": 264.12
  },
  "metadados": {
    "engine": "EasyOCR",
    "confianca_media": 85.5,
    "decisao": {
      "engine_escolhida": "EasyOCR",
      "motivo": "Confiança suficiente",
      "tentativas": ["easyocr"]
    }
  }
}
```

## 🧠 Lógica de Decisão

### Quando usa cada engine?

```python
# NÍVEL 1: EasyOCR (sempre primeiro)
if confiança >= 70% AND produtos >= 5:
    return resultado_easyocr  # Suficiente!

# Se usuário escolheu modo grátis
if modo == "gratis":
    return resultado_easyocr  # Mesmo com baixa confiança

# NÍVEL 2: Google Vision (se configurado)
if google_disponivel():
    resultado = processar_google()
    if produtos >= 5:
        return resultado

# NÍVEL 3: Claude Vision (último recurso)
if modo == "premium" AND claude_disponivel():
    return processar_claude()  # Máxima precisão

# Fallback
return melhor_resultado_disponível
```

## 💰 Estimativa de Custos

### Cenário: 1.000 notas/mês

| Tipo Nota | % | Qtd | Engine Usado | Custo Unitário | Custo Total |
|-----------|---|-----|--------------|----------------|-------------|
| Fáceis (boa qualidade) | 70% | 700 | EasyOCR | $0 | **$0** |
| Médias (qualidade OK) | 25% | 250 | Google | $0* | **$0*** |
| Difíceis (borradas) | 5% | 50 | Claude | $0.04 | **$2** |
| **TOTAL** | 100% | 1000 | - | - | **~$2/mês** |

*Google: 1.000 primeiras são grátis

### Comparação com Alternativas

| Solução | Custo para 1.000 notas |
|---------|------------------------|
| **Sistema Híbrido** | $2 |
| Só Tesseract | $0 (mas ~50% precisão) |
| Só Google Vision | $1.50 |
| Só Claude Vision | $40 |

## 🎯 Quando Usar Cada Modo?

### Modo Grátis (`modo=gratis`)
✅ **Use quando**:
- Usuário não quer gastar nada
- Nota fiscal simples e limpa
- Desenvolvimento e testes
- App está offline

❌ **Não use quando**:
- Nota muito borrada
- Muitos produtos pequenos
- Precisão crítica

### Modo Automático (padrão)
✅ **Use quando**:
- Melhor custo-benefício
- Não sabe a qualidade da nota
- Quer otimizar custos
- **RECOMENDADO para produção**

### Modo Premium (`modo=premium`)
✅ **Use quando**:
- Precisão é crítica
- Nota muito complexa
- Usuário pagou por premium
- Importação de dados históricos

## 📈 Melhorando a Precisão

### 1. Qualidade da Foto

**BOM** ✅:
- Boa iluminação natural
- Nota fiscal plana (sem dobras)
- Foto de frente (90°)
- Resolução mínima 1080p
- Fundo contrastante

**RUIM** ❌:
- Foto escura ou muito clara
- Nota amassada ou dobrada
- Ângulo inclinado
- Foto borrada/tremida
- Reflexo de luz

### 2. Preparação da Imagem

Se possível, pré-processar antes de enviar:

```python
from PIL import Image, ImageEnhance

# Aumentar contraste
img = Image.open('nota.jpg')
enhancer = ImageEnhance.Contrast(img)
img_melhorada = enhancer.enhance(1.5)
img_melhorada.save('nota_melhorada.jpg')
```

### 3. Formato Recomendado

- **Formato**: JPEG ou PNG
- **Resolução**: 1920x1080 ou maior
- **Tamanho**: < 5MB
- **Orientação**: Portrait (vertical)

## 🔍 Debugging

### Ver Confiança do OCR

```bash
curl -X POST http://localhost:8000/api/ocr-inteligente \
  -F "file=@nota.jpg" \
  -F "modo=gratis" | jq '.confianca'
```

### Forçar Engine Específico

```python
# Testar só EasyOCR
resultado = ocr.processar_nota_fiscal(
    imagem_bytes=img_bytes,
    modo_forcado="easyocr"
)

# Testar só Claude
resultado = ocr.processar_nota_fiscal(
    imagem_bytes=img_bytes,
    modo_forcado="claude"
)
```

### Ver Log de Decisão

```json
{
  "metadados": {
    "decisao": {
      "engine_escolhida": "EasyOCR",
      "motivo": "Confiança suficiente",
      "confianca": 85.5,
      "tentativas": ["easyocr"]
    }
  }
}
```

## 🚀 Próximos Passos

### Implementações Futuras

- [ ] Adicionar Google Cloud Vision
- [ ] Cache de resultados (nota já processada)
- [ ] Processamento em batch
- [ ] Preview antes de confirmar
- [ ] Edição manual de produtos
- [ ] Histórico de OCRs
- [ ] Estatísticas de uso por engine
- [ ] A/B testing de engines

### Otimizações

- [ ] Compressão de imagem antes de enviar
- [ ] Processamento assíncrono (workers)
- [ ] Queue para processar em background
- [ ] Retry automático em caso de falha

## 🎓 Arquivos do Sistema

```
app/utils/
├── easyocr_processor.py       # Engine EasyOCR
├── claude_vision_ocr.py        # Engine Claude Vision
├── ocr_hibrido.py             # Sistema inteligente
└── ocr_nota_fiscal.py         # Tesseract (legado)

app/api/
└── main.py                    # Endpoint /api/ocr-inteligente
```

## 💡 Dicas de Produção

### 1. Monitorar Uso

```python
# Adicionar métricas
from collections import Counter

engines_usados = Counter()

# No endpoint
engine = resultado['engine_usada']
engines_usados[engine] += 1

# Ver estatísticas
print(engines_usados)
# Counter({'EasyOCR': 700, 'Google': 250, 'Claude': 50})
```

### 2. Limitar Uso de Claude

```python
# Limitar Claude a X por dia
CLAUDE_MAX_DIARIO = 100
claude_hoje = contar_claude_hoje()

if claude_hoje >= CLAUDE_MAX_DIARIO:
    usar_google_ou_easyocr()
```

### 3. Fallback Gracioso

```python
try:
    resultado = ocr_hibrido.processar()
except Exception:
    # Se tudo falhar, tentar Tesseract legado
    resultado = ocr_tesseract.processar()
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique logs do servidor
2. Teste com `modo=gratis` primeiro
3. Valide qualidade da imagem
4. Verifique se EasyOCR instalou corretamente

---

**Desenvolvido com ❤️**
**Versão**: 1.0.0
**Data**: 31/10/2025
**Status**: ✅ Funcionando
