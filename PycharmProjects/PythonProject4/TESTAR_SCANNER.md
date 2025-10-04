# 🔧 Testando o Scanner - Troubleshooting

## ❌ Problema: "Não consigo arrastar imagens"

### 🔍 **Passo 1: Verificar se o scanner carregou**

1. Abra http://localhost:8000/scanner.html
2. Pressione **F12** (abre o console do navegador)
3. Olhe a aba **"Console"**

**Você DEVE ver:**
```
Configurando eventos do scanner...
✓ Click event configurado
✓ Change event configurado
✓ Drag and drop configurado
```

**Se NÃO ver isso:**
- ❌ JavaScript não carregou
- ❌ Caminho do arquivo errado
- ❌ Erro no código

### 🔍 **Passo 2: Limpar cache do navegador**

**Chrome/Edge:**
1. Pressione **Ctrl + Shift + Delete**
2. Selecione "Imagens e arquivos em cache"
3. Clique "Limpar dados"
4. Recarregue a página (**Ctrl + F5**)

**Firefox:**
1. Pressione **Ctrl + Shift + Delete**
2. Selecione "Cache"
3. Clique "Limpar agora"
4. Recarregue (**Ctrl + F5**)

### 🔍 **Passo 3: Testar clique no upload**

1. **Clique na área cinza** "📋 Clique aqui..."
2. **No console deve aparecer:** `Upload area clicada`
3. **Janela de seleção de arquivo deve abrir**

**Se não abrir:**
- Cache não foi limpo
- JavaScript com erro

### 🔍 **Passo 4: Testar drag and drop**

1. **Arraste UMA imagem** sobre a área cinza
2. **No console deve aparecer:** `Dragging over...`
3. **Solte a imagem**
4. **No console deve aparecer:** `Drop event! Files: 1`

**Se não aparecer:**
- Navegador bloqueando
- JavaScript com erro

### 🔍 **Passo 5: Verificar validação de arquivo**

Quando selecionar/arrastar arquivo, console mostra:
```
Arquivo selecionado: nota.jpg image/jpeg 245678
Arquivo aceito e armazenado
Preview carregado, botões habilitados
```

## ✅ **Solução Rápida:**

### **Método 1: Forçar reload completo**
```
Ctrl + Shift + R  (ou Cmd + Shift + R no Mac)
```

### **Método 2: Usar modo anônimo**
1. **Chrome:** Ctrl + Shift + N
2. **Firefox:** Ctrl + Shift + P
3. Acesse: http://localhost:8000/scanner.html
4. Teste novamente

### **Método 3: Outro navegador**
- Se está no Chrome, teste no Firefox
- Se está no Firefox, teste no Chrome

## 🐛 **Erros Comuns:**

### **"Por favor, selecione uma imagem válida"**
- ✅ Só aceita: JPG, JPEG, PNG, GIF, BMP, WEBP
- ❌ NÃO aceita: PDF, DOC, TXT

### **"Imagem muito grande"**
- ✅ Máximo: 10MB
- ❌ Reduza o tamanho da imagem

### **Nada acontece ao clicar**
- Limpe o cache
- Recarregue com Ctrl + F5
- Veja erros no console (F12)

## 🔬 **Debug Manual:**

### **1. Verificar elementos HTML:**
Console do navegador:
```javascript
console.log('uploadArea:', document.getElementById('uploadArea'));
console.log('fileInput:', document.getElementById('fileInput'));
console.log('scanBtn:', document.getElementById('scanBtn'));
console.log('debugBtn:', document.getElementById('debugBtn'));
```

Todos devem retornar elementos, não `null`.

### **2. Testar manualmente:**
Console do navegador:
```javascript
// Simular clique
document.getElementById('uploadArea').click();

// Ver arquivo selecionado
console.log(selectedFile);
```

### **3. Verificar se API está OK:**
```bash
curl http://localhost:8000/api
```

Deve retornar JSON da API.

## 📋 **Checklist:**

- [ ] Cache limpo (Ctrl + Shift + Delete)
- [ ] Página recarregada (Ctrl + F5)
- [ ] Console sem erros (F12)
- [ ] Mensagens de log aparecem
- [ ] Área de upload responde ao clique
- [ ] Drag and drop funciona
- [ ] Arquivo é reconhecido
- [ ] Preview aparece
- [ ] Botões habilitados

## 🚀 **Se tudo falhar:**

### **Reinicie o servidor:**
```bash
./stop_app.sh
./start_app.sh
```

### **Teste direto sem navegador:**
```bash
# Testar API
curl -X POST http://localhost:8000/api/debug-ocr \
  -F "file=@sua_nota.jpg"
```

### **Acesse URL alternativa:**
```
http://localhost:8080/scanner.html
```

## 💡 **Dica Final:**

**O problema mais comum é CACHE!**

1. **Ctrl + Shift + Delete** (limpar cache)
2. **Ctrl + F5** (reload forçado)
3. Tente novamente

**OU**

1. Modo anônimo (**Ctrl + Shift + N**)
2. Acesse o scanner
3. Teste

---

**Se AINDA não funcionar, me avise e vejo os logs detalhados do console!**
