# 📸 Como Usar o Scanner de Nota Fiscal

## 🚀 Passo a Passo Completo

### **1. Acesse o Scanner**
```
http://localhost:8000/scanner.html
```
ou
```
http://localhost:8080/scanner.html
```

### **2. Faça Login (Recomendado)**
⚠️ **IMPORTANTE:** Faça login ANTES de escanear para ganhar tokens!

**Como fazer login:**
1. Volte para a página principal: http://localhost:8000
2. No menu lateral esquerdo, faça login com CPF e senha
3. Volte para o scanner: http://localhost:8000/scanner.html

**Por que fazer login?**
- ✅ Ganha **10 tokens por produto** extraído
- ✅ Seus dados ficam salvos no seu perfil
- ✅ Pode ver histórico de contribuições

### **3. Envie a Foto da Nota**

**Opção A: Clicar**
1. Clique na área cinza "📋 Clique aqui ou arraste a foto"
2. Selecione a foto da nota fiscal
3. Preview aparece

**Opção B: Arrastar**
1. Arraste a foto da nota para a área cinza
2. Preview aparece

### **4. Escolha o Que Fazer**

Agora você tem **2 botões:**

#### 🔍 **Botão 1: Debug OCR (Ver Texto Extraído)**
**Use para:** Ver o que o OCR está lendo
- ✅ Mostra texto completo extraído
- ✅ Mostra supermercado identificado
- ✅ Mostra data encontrada
- ✅ Mostra produtos extraídos
- ✅ Mostra dicas de melhoria
- ❌ **NÃO salva no banco**

**Quando usar:**
- Primeira vez com uma nota nova
- Quer ver se está reconhecendo bem
- Quer diagnosticar problemas

#### 📸 **Botão 2: Escanear Nota Fiscal**
**Use para:** Salvar os produtos no banco
- ✅ Extrai todos os dados
- ✅ **SALVA no banco de dados**
- ✅ Ganha tokens (se logado)
- ✅ Mostra resumo do que foi salvo

**Quando usar:**
- Já viu que está reconhecendo bem (com Debug)
- Quer salvar os produtos no banco
- Quer ganhar tokens

### **5. Clique em "📸 Escanear Nota Fiscal"**

**O que acontece:**
1. ⏳ Aparecer "Processando nota fiscal..."
2. 🔍 Sistema extrai texto da imagem
3. 🏪 Identifica supermercado
4. 📅 Encontra data
5. 📦 Extrai produtos e preços
6. 💾 **SALVA tudo no banco**
7. ✅ Mostra resultado!

### **6. Veja o Resultado**

**Tela de Resultado mostra:**
```
✅ Nota Fiscal Processada!

🏪 Loja dos Descontos
📦 3 produtos
📅 03/04/2013
💰 Total: R$ 21,71

Produtos Extraídos:
• Desod Sanit Pinh-Sanifeci - R$ 2.09
• Batata Palha Sli-Micos - R$ 6.88
• X4Bebida Lactea -Pauli - R$ 2.44

💎 Você ganhou 30 tokens!
```

### **7. Verifique no Banco**

**Produtos foram salvos! Você pode:**

1. **Buscar no app principal:**
   - Vá para http://localhost:8000
   - Busque por "desodorante" ou "batata"
   - Verá os produtos que escaneou!

2. **Ver contribuições:**
   - Menu lateral → "Ver Contribuições"
   - Verá suas notas escaneadas

3. **Checar carteira:**
   - Menu lateral mostra tokens ganhos
   - Cada produto = 10 tokens!

## 🎯 Fluxo Completo Recomendado

```
1. FAZER LOGIN
   ↓
2. IR PARA SCANNER
   ↓
3. ENVIAR FOTO
   ↓
4. CLICAR "DEBUG OCR" (primeira vez)
   ↓
5. VER O QUE FOI EXTRAÍDO
   ↓
6. SE ESTIVER BOM → CLICAR "ESCANEAR"
   ↓
7. GANHAR TOKENS!
   ↓
8. VER PRODUTOS NO APP
```

## ❓ Perguntas Frequentes

### **"Não vejo os botões!"**
- ✅ Certifique-se que enviou a foto
- ✅ Preview da imagem deve aparecer
- ✅ Botões ficam abaixo do preview

### **"Cliquei mas nada acontece!"**
- ✅ Verifique se API está rodando: http://localhost:8000/api
- ✅ Veja o console do navegador (F12)
- ✅ Tente recarregar a página

### **"Diz que não encontrou produtos!"**
- ✅ Use o "Debug OCR" para ver o texto
- ✅ Tire foto mais nítida
- ✅ Melhore iluminação

### **"Não ganho tokens!"**
- ✅ Faça login ANTES de escanear
- ✅ Tokens aparecem na carteira (menu lateral)

### **"Como vejo os produtos salvos?"**
```bash
# Ver no terminal:
python3 verificar_banco.py
```

Ou busque no app principal!

## 🔍 Teste Rápido

### **1. Teste com texto:**
```bash
python3 testar_minha_nota.py
```

### **2. Teste no app:**
1. Vá para http://localhost:8000/scanner.html
2. Faça upload da foto
3. Clique "Debug OCR" → vê o que foi extraído
4. Clique "Escanear" → salva no banco
5. Volte para app principal e busque os produtos!

## ✅ Confirmação de Sucesso

**Você saberá que funcionou quando:**

1. ✅ Ver tela "Nota Fiscal Processada!"
2. ✅ Ver lista de produtos extraídos
3. ✅ Ver "Você ganhou X tokens!"
4. ✅ Carteira atualizada (se logado)
5. ✅ Produtos aparecem nas buscas

## 🎁 Recompensas

Por nota fiscal escaneada:
- 📦 **10 tokens por produto**
- 💾 **Dados salvos** no banco
- 📊 **Estatísticas** atualizadas
- 🏆 **Contribuição** para a comunidade

**Exemplo:**
- Nota com 5 produtos = **50 tokens!**
- Nota com 10 produtos = **100 tokens!**

## 🚀 Começe Agora!

1. **Abra:** http://localhost:8000/scanner.html
2. **Faça login** (no app principal)
3. **Envie foto** da nota
4. **Clique** "📸 Escanear Nota Fiscal"
5. **Ganhe tokens!** 💰

---

**💡 Dica:** Use sempre o "Debug OCR" primeiro para ver se está reconhecendo bem!
