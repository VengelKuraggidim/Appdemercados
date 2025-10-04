# 📸 Scanner de Nota Fiscal - Guia Completo

Sistema de reconhecimento OCR para extrair produtos e preços de notas fiscais de supermercado.

## 🎯 Como Funciona

1. **Tire uma foto da nota fiscal** do supermercado
2. **Sistema extrai automaticamente** todos os produtos e preços
3. **Ganha tokens** por cada produto extraído (10 tokens por produto!)
4. **Dados salvos** no banco com geolocalização (se disponível)

## 📋 Recursos

### ✅ O que o sistema reconhece:
- ✅ **Produtos e preços** - Extrai nome e valor de cada item
- ✅ **Supermercado** - Identifica automaticamente (Carrefour, Pão de Açúcar, Atacadão, etc.)
- ✅ **Data da compra** - Reconhece a data da nota
- ✅ **Total da compra** - Valida o total com a soma dos produtos
- ✅ **Quantidade** - Identifica quantidade de cada produto

### 🏪 Supermercados suportados:
- Carrefour
- Pão de Açúcar
- Extra
- Atacadão
- Dia%
- Assaí
- Walmart
- Big
- Mambo

## 🚀 Como Usar

### 1. **Instalar Tesseract OCR** (necessário)

No Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

No macOS:
```bash
brew install tesseract tesseract-lang
```

No Windows:
- Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
- Instale e adicione ao PATH

### 2. **Instalar dependências Python**
```bash
pip install pytesseract Pillow
```

### 3. **Acessar o Scanner**
1. Abra o app: `http://localhost:8000`
2. Clique em **"📸 Escanear Nota Fiscal"** na barra lateral
3. Tire foto ou faça upload da nota fiscal
4. Aguarde o processamento
5. Revise os produtos extraídos

## 📱 Interface do Scanner

### Página: `/scanner.html`
- **Upload simples** - Clique ou arraste a foto
- **Preview da imagem** - Veja antes de processar
- **Resultados detalhados**:
  - Lista de produtos extraídos
  - Supermercado identificado
  - Data da compra
  - Total da nota
  - Tokens ganhos

## 🔧 API Endpoints

### 1. **Escanear Nota Fiscal (com salvamento)**
```
POST /api/escanear-nota-fiscal
Content-Type: multipart/form-data

Params:
- file: arquivo de imagem (JPG, PNG)
- usuario_nome: nome do usuário (opcional)
- latitude: latitude (opcional)
- longitude: longitude (opcional)
- endereco: endereço do supermercado (opcional)

Response:
{
  "sucesso": true,
  "mensagem": "✅ 15 produtos extraídos da nota fiscal!",
  "supermercado": "carrefour",
  "data_compra": "2025-10-03T00:00:00",
  "total_produtos": 15,
  "produtos_salvos": [...],
  "total_nota": 125.50,
  "soma_produtos": 125.30,
  "verificado": true,
  "confianca": 85.0,
  "tokens_ganhos": 150
}
```

### 2. **Preview (sem salvar)**
```
POST /api/preview-nota-fiscal
Content-Type: multipart/form-data

Params:
- file: arquivo de imagem

Response:
{
  "sucesso": true,
  "supermercado": "carrefour",
  "produtos": [
    {
      "nome": "ARROZ TIPO 1",
      "preco": 15.90,
      "quantidade": 1.0
    },
    ...
  ],
  "total_nota": 125.50,
  "confianca": 85.0
}
```

## 💡 Dicas para Melhores Resultados

### ✅ Faça:
1. **Foto nítida** - Evite fotos tremidas ou borradas
2. **Boa iluminação** - Luz natural ou boa iluminação artificial
3. **Nota fiscal completa** - Capture toda a nota, especialmente a lista de produtos
4. **Foco nos produtos** - Certifique-se que a área dos produtos está legível
5. **Nota reta** - Tente manter a nota o mais reta possível

### ❌ Evite:
1. **Sombras** - Podem dificultar a leitura
2. **Reflexos** - Especialmente em notas plastificadas
3. **Fotos de longe** - Diminui a qualidade do texto
4. **Notas amassadas** - Dificultam o reconhecimento

## 🎁 Sistema de Recompensas

### Ganhe tokens ao escanear notas:
- **10 tokens** por produto extraído
- **Bônus de verificação** se o total bater (alta confiança)
- **Geolocalização** adiciona valor aos dados

### Exemplo:
- Nota com 15 produtos = **150 tokens**!
- Use tokens para fazer buscas no app

## 🔍 Como o OCR Funciona

### Processo:
1. **Recebe imagem** da nota fiscal
2. **Pré-processa** - Converte para escala de cinza
3. **Extrai texto** - Usa Tesseract OCR
4. **Identifica supermercado** - Por padrões conhecidos
5. **Extrai produtos** - Regex para formato "NOME PREÇO"
6. **Valida total** - Compara soma com total da nota
7. **Salva no banco** - Com todos os dados

### Padrões reconhecidos:
```
ARROZ TIPO 1          15,90
001 FEIJAO PRETO      8.50
OLEO DE SOJA 1L       R$ 7.90
```

## 🐛 Troubleshooting

### Problema: "Tesseract não encontrado"
**Solução:** Instale o Tesseract OCR:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-por
```

### Problema: "Nenhum produto encontrado"
**Soluções:**
1. Tire uma foto mais nítida
2. Melhore a iluminação
3. Certifique-se que a lista de produtos está visível
4. Tente com outra nota fiscal

### Problema: "Total não bate"
- Normal se a nota tiver descontos/taxas
- Sistema marca como "não verificado" mas salva os dados
- Confiança pode ser menor

### Problema: "Supermercado não identificado"
- Sistema salva como "Não identificado"
- Você pode editar manualmente depois
- Adicione o nome do supermercado aos padrões

## 📊 Vantagens sobre Scraping

### Por que usar scanner de notas?
1. **✅ Dados reais** - Preços verdadeiros de compras reais
2. **✅ Não depende de sites** - Funciona offline
3. **✅ Múltiplos produtos** - Uma foto = vários preços
4. **✅ Data precisa** - Sabe exatamente quando foi a compra
5. **✅ Sem bloqueios** - Não depende do Google/sites
6. **✅ Geolocalização** - Sabe onde foi a compra

## 🚀 Próximos Passos

### Melhorias planejadas:
- [ ] OCR mais preciso com ML/AI
- [ ] Reconhecer códigos de barras
- [ ] Integrar com NFC-e (nota fiscal eletrônica)
- [ ] Suporte a mais formatos de nota
- [ ] Reconhecimento de promoções/descontos
- [ ] Dashboard de estatísticas de compras

## 📝 Estrutura de Arquivos

```
app/
├── utils/
│   └── ocr_nota_fiscal.py      # Módulo OCR principal
├── api/
│   └── main.py                 # Endpoints da API
frontend/
├── scanner.html                # Interface do scanner
└── src/
    └── scanner.js              # Lógica do frontend
```

## 🎯 Conclusão

O scanner de notas fiscais é a forma **mais eficiente** de alimentar o banco de dados:
- ✅ Rápido (1 foto = vários produtos)
- ✅ Preciso (dados reais de compras)
- ✅ Recompensador (muitos tokens!)
- ✅ Confiável (não depende de scraping)

**Incentive os usuários a usar o scanner!** 📸
