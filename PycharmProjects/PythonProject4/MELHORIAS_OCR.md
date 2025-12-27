# 🔍 Melhorias no OCR - Guia de Debug e Ajustes

## O que foi melhorado

### 1. **Qualidade de Imagem**
- ✅ Aumento de contraste (2x)
- ✅ Aumento de nitidez (2x)
- ✅ Conversão otimizada para escala de cinza

### 2. **Extração de Data**
- ✅ Múltiplos padrões de data (DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)
- ✅ Busca contextual (próximo a palavras como DATA, EMISSÃO, CUPOM)
- ✅ Validação de datas (1-31 dias, 1-12 meses, 2000-2030 anos)

### 3. **Extração de Produtos**
- ✅ 4 padrões diferentes de regex
- ✅ Filtragem de palavras-chave (TOTAL, SUBTOTAL, etc.)
- ✅ Suporte a múltiplos formatos:
  - Código + Nome + Quantidade + Preço
  - Nome + Quantidade + Preço
  - Nome + Preço
- ✅ Capitalização automática dos nomes
- ✅ Validação de preços (0.10 a 1000)

### 4. **Debug Tool** 🆕
- ✅ Botão "Debug OCR" no scanner
- ✅ Mostra texto completo extraído
- ✅ Identifica o que foi reconhecido
- ✅ Mostra primeiras 30 linhas
- ✅ Dicas para melhorar

## 🔧 Como usar o Debug

### Passo 1: Escanear com Debug
1. Acesse `/scanner.html`
2. Faça upload da nota fiscal
3. Clique em **"🔍 Debug OCR (Ver Texto Extraído)"**

### Passo 2: Analisar o Resultado
O debug mostra:

**📊 Resumo:**
- Supermercado identificado (ou não)
- Data identificada (ou não)
- Quantidade de produtos
- Total encontrado
- Total de linhas

**📦 Produtos:**
- Primeiros 5 produtos extraídos
- Nome, preço e quantidade

**📝 Texto Bruto:**
- Primeiras 30 linhas extraídas pelo OCR
- **Use isso para ajustar os padrões regex!**

### Passo 3: Ajustar Padrões (se necessário)

Se o OCR não está reconhecendo corretamente, edite `app/utils/ocr_nota_fiscal.py`:

#### Adicionar novo supermercado:
```python
SUPERMERCADOS = {
    'CARREFOUR': 'carrefour',
    'NOVO_MERCADO': 'novo_mercado',  # Adicione aqui
    ...
}
```

#### Adicionar novo padrão de produto:
```python
padroes = [
    # Seus padrões atuais...

    # Novo padrão
    r'^SEU_PADRAO_AQUI',
]
```

#### Adicionar novo padrão de data:
```python
padroes = [
    # Padrões atuais...

    # Novo formato
    r'(\d{4})[/\-\.](\d{2})[/\-\.](\d{2})',  # YYYY/MM/DD
]
```

## 📸 Dicas para Melhores Fotos

### ✅ Faça:
1. **Boa iluminação** - Luz natural ou ambiente bem iluminado
2. **Foto nítida** - Segure firme, sem tremer
3. **Nota reta** - Tente manter a nota o mais reta possível
4. **Foco nos produtos** - Garanta que a lista de produtos está legível
5. **Zoom adequado** - Nem muito perto, nem muito longe

### ❌ Evite:
1. **Sombras** - Podem escurecer partes importantes
2. **Reflexos** - Em notas plastificadas
3. **Amassados** - Dificulta muito o OCR
4. **Fotos de longe** - Perde-se detalhe
5. **Iluminação amarelada** - Pode afetar contraste

## 🎯 Resolução de Problemas Comuns

### Problema 1: Supermercado não identificado
**Diagnóstico:**
1. Use o Debug OCR
2. Veja se o nome do supermercado aparece no texto extraído
3. Verifique se está no dicionário `SUPERMERCADOS`

**Solução:**
```python
# Adicione variações do nome
SUPERMERCADOS = {
    'NOME COMPLETO': 'slug',
    'NOME': 'slug',
    'SIGLA': 'slug',
}
```

### Problema 2: Data não encontrada
**Diagnóstico:**
1. Use o Debug OCR
2. Procure a data nas primeiras 30 linhas
3. Veja qual formato está sendo usado

**Solução:**
Adicione o padrão específico em `extrair_data()`:
```python
# Exemplo: se a data aparece como "03/10/2025"
r'(\d{2})/(\d{2})/(\d{4})',
```

### Problema 3: Poucos produtos extraídos
**Diagnóstico:**
1. Use o Debug OCR
2. Veja quais linhas têm produtos
3. Identifique o formato usado

**Soluções:**
- **Foto de baixa qualidade** → Tire outra foto
- **Formato diferente** → Adicione novo padrão regex
- **Produtos filtrados** → Ajuste validações de preço

### Problema 4: Produtos com nomes errados
**Diagnóstico:**
1. Veja o texto bruto no Debug
2. Identifique onde está o erro (OCR ou regex)

**Soluções:**
- **Erro de OCR** → Melhore qualidade da foto
- **Erro de regex** → Ajuste padrão de captura

## 🔬 Testando Melhorias

### Ciclo de teste:
1. **Tire foto** de uma nota fiscal
2. **Use Debug OCR** para ver o texto extraído
3. **Identifique problemas** (supermercado, data, produtos)
4. **Ajuste código** em `ocr_nota_fiscal.py`
5. **Reinicie o app**
6. **Teste novamente**

### Endpoint de teste direto:
```bash
# Debug OCR via curl
curl -X POST "http://localhost:8000/api/debug-ocr" \
  -F "file=@nota_fiscal.jpg"
```

## 📈 Métricas de Qualidade

### Bom resultado:
- ✅ Supermercado identificado
- ✅ Data identificada
- ✅ 80%+ dos produtos extraídos
- ✅ Total validado (diferença < 5%)
- ✅ Confiança > 70%

### Resultado ruim:
- ❌ Supermercado não identificado
- ❌ Data não encontrada
- ❌ < 50% dos produtos
- ❌ Total não bate
- ❌ Confiança < 40%

## 🚀 Próximos Passos

### Melhorias planejadas:
1. **Machine Learning** - Treinar modelo específico para notas fiscais
2. **OCR Cloud** - Usar Google Vision ou AWS Textract
3. **Pré-processamento avançado** - Rotação automática, desfoque
4. **Validação de produtos** - Conferir com banco de dados
5. **Correção automática** - Sugerir correções baseadas em histórico

## 📚 Recursos Úteis

### Regex testers:
- https://regex101.com/
- https://regexr.com/

### OCR alternatives:
- Google Cloud Vision API
- AWS Textract
- Microsoft Azure OCR
- EasyOCR (Python)

### Tesseract docs:
- https://github.com/tesseract-ocr/tesseract
- https://tesseract-ocr.github.io/

---

**Dica:** Use sempre o Debug OCR antes de ajustar o código. Ele mostra exatamente o que o Tesseract está extraindo!
