# 📸 Sistema de Contribuição por Foto + OCR

## 🎯 Funcionalidade Implementada

Agora você pode **tirar uma foto do preço** e o sistema reconhece automaticamente:
- ✅ **Preço** (R$ 12,90)
- ✅ **Produto** (Arroz, Feijão, etc)
- ✅ **Marca** (Tio João, Camil, etc)
- ✅ **Localização automática** (via GPS do celular)

## 🚀 Como Usar

### 1. Acesse a página de foto:
```
http://localhost:3000/foto.html
```

### 2. Tire ou escolha uma foto:
- **Opção A**: Clique para escolher foto da galeria
- **Opção B**: Tire foto na hora (em dispositivos móveis)
- **Opção C**: Arraste e solte uma imagem

### 3. Sistema analisa automaticamente:
- Extrai o preço da imagem
- Identifica produto e marca (se possível)
- Pega sua localização automaticamente

### 4. Confirme e envie:
- Adicione o nome do supermercado
- Adicione observações (opcional)
- Clique em "Confirmar e Enviar"

## 🧠 Como Funciona o OCR

### Backend (Python):

```python
# app/utils/ocr.py
- Usa EasyOCR ou Tesseract
- Extrai texto da imagem
- Identifica padrões de preço (R$ 12,90)
- Reconhece produtos comuns
- Identifica marcas conhecidas
```

### Frontend (JavaScript):

```javascript
// frontend/src/foto.js
- Acessa câmera do dispositivo
- Captura ou seleciona foto
- Obtém geolocalização do usuário
- Envia para API processar
- Mostra resultados extraídos
```

## 📱 Geolocalização Automática

O sistema pede permissão para:
1. Acessar sua localização GPS
2. Converte coordenadas em cidade/bairro
3. Adiciona automaticamente à contribuição

**Exemplo**: "São Paulo - Paulista" ou "Rio de Janeiro - Copacabana"

## 🔧 Configuração (Opcional - Para Melhor Precisão)

### Opção 1: EasyOCR (Recomendado - Mais Preciso)

```bash
pip install easyocr
```

**Vantagens:**
- Melhor precisão
- Múltiplos idiomas
- Não precisa instalar Tesseract

**Desvantagens:**
- Download de ~500MB (modelos de IA)
- Mais lento no primeiro uso

### Opção 2: Tesseract OCR (Mais Leve)

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por

# MacOS
brew install tesseract tesseract-lang

# Windows
# Baixe de: https://github.com/UB-Mannheim/tesseract/wiki

pip install pytesseract
```

### Sem OCR (Fallback)

Se não instalar nenhum OCR, o sistema ainda funciona mas:
- Não extrai dados automaticamente
- Usuário precisa digitar manualmente

## 📊 Endpoints da API

### 1. Extrair dados de foto
```bash
POST /api/extrair-preco-foto
Content-Type: multipart/form-data

file: (image file)

Response:
{
  "sucesso": true,
  "preco": 12.90,
  "produto_nome": "arroz",
  "marca": "Tio João",
  "precos_encontrados": [12.90, 5.50],
  "texto_extraido": "Arroz Tio João R$ 12,90...",
  "confianca": 0.8
}
```

### 2. Contribuir com foto
```bash
POST /api/contribuir-com-foto
Content-Type: multipart/form-data

file: (image file)
supermercado: "Carrefour"
localizacao: "São Paulo - Centro" (opcional)
observacao: "Promoção" (opcional)
usuario_nome: "João" (opcional)

Response:
{
  "sucesso": true,
  "mensagem": "Contribuição adicionada!",
  "contribuicao": { ... },
  "dados_extraidos": { ... }
}
```

## 🎨 Interface

### Página de Foto (`/foto.html`):

- **Área de Upload**: Drag & drop ou clique
- **Preview**: Mostra foto antes de processar
- **Análise**: Botão para processar com OCR
- **Resultados**: Mostra dados extraídos
- **Confirmação**: Formulário para confirmar
- **Localização**: GPS automático

## 🧪 Testando o Sistema

### Teste 1: Com Foto Real

1. Tire foto de um preço no supermercado
2. Acesse http://localhost:3000/foto.html
3. Faça upload da foto
4. Clique em "Analisar Foto"
5. Veja os dados extraídos!

### Teste 2: Com Imagem de Teste

Crie uma imagem simples com texto:

```
Arroz Tio João 5kg
R$ 23,90
```

Salve como JPG e faça upload!

### Teste 3: Via API

```bash
curl -X POST http://localhost:8000/api/extrair-preco-foto \
  -F "file=@foto_preco.jpg"
```

## 📋 Produtos Reconhecidos Automaticamente

O OCR identifica:

**Produtos:**
- Arroz
- Feijão
- Café
- Açúcar
- Óleo
- Leite
- Macarrão
- Sal
- Farinha

**Marcas:**
- Tio João
- Camil
- Pilão
- União
- Liza
- Italac
- Nestlé
- Barilla
- E mais...

## 💡 Dicas para Melhores Resultados

### ✅ Faça:
- Tire foto com boa iluminação
- Foque no preço (nítido)
- Foto reta (não inclinada)
- Aproxime da etiqueta de preço

### ❌ Evite:
- Fotos escuras ou muito claras
- Texto desfocado
- Reflexos na etiqueta
- Fotos muito longe

## 🔒 Privacidade

- **Fotos não são salvas permanentemente**
- Apenas dados extraídos (preço, produto) são salvos
- Localização é opcional
- Pode usar sem informar seu nome

## 🚀 Próximas Melhorias

- [ ] Salvar fotos completas para moderação
- [ ] Treinar modelo específico para etiquetas de preço
- [ ] Reconhecer códigos de barras
- [ ] Detectar promoções automaticamente
- [ ] OCR em panfletos inteiros
- [ ] Suporte para múltiplos produtos em uma foto

## 📈 Fluxo Completo

```
1. Usuário tira foto do preço
   ↓
2. JavaScript pega geolocalização
   ↓
3. Foto enviada para API
   ↓
4. OCR extrai texto da imagem
   ↓
5. Regex identifica preços (R$ X,XX)
   ↓
6. IA identifica produto e marca
   ↓
7. Retorna dados para usuário
   ↓
8. Usuário confirma/corrige
   ↓
9. Salva no banco de dados
   ↓
10. Disponível para todos!
```

## 🎉 Resultado

Agora você tem um sistema onde:
- ✅ Tire foto → Sistema reconhece → Dados salvos automaticamente
- ✅ GPS automático da localização
- ✅ Interface mobile-friendly
- ✅ Reconhecimento inteligente de preços
- ✅ Suporte para câmera e galeria
- ✅ Feedback visual em tempo real

**É só tirar foto e enviar! 📸💰**

---

## 🌐 Links Úteis

- **Adicionar por Foto**: http://localhost:3000/foto.html
- **Adicionar Manual**: http://localhost:3000/contribuir.html
- **Ver Contribuições**: http://localhost:3000/contribuicoes.html
- **Buscar Preços**: http://localhost:3000/
- **API Docs**: http://localhost:8000/docs
