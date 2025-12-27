# 💾 Persistência de Dados - Comparador de Preços

## ✅ Garantia de Armazenamento Permanente

Todas as contribuições feitas no aplicativo **são salvas permanentemente** em um banco de dados SQLite e **NÃO dependem do cache do navegador**.

### 🔒 Como funciona:

1. **Banco de Dados SQLite** (`precos.db`)
   - Arquivo físico salvo em: `/home/vengel/PycharmProjects/PythonProject4/precos.db`
   - Tamanho atual: ~40KB
   - Armazena todos os produtos e preços

2. **Contribuições Manuais**
   - Quando você adiciona um preço, ele é salvo no banco
   - Marcado com `manual = True`
   - Inclui: nome do usuário, localização, observação, foto (se houver)

3. **Independente do Navegador**
   - ✅ Limpar cache do navegador → Dados permanecem
   - ✅ Limpar cookies → Dados permanecem
   - ✅ Fechar navegador → Dados permanecem
   - ✅ Reiniciar computador → Dados permanecem
   - ✅ Trocar de navegador → Dados permanecem

## 📊 Estatísticas Atuais

```
Total de produtos: 18
Total de preços: 37
Contribuições manuais: 37
```

## 🔍 Como Verificar os Dados

Execute o script de verificação:

```bash
python verificar_banco.py
```

## 💾 Backup Recomendado

Para garantir segurança extra, faça backup regular do arquivo:

```bash
# Backup manual
cp precos.db precos.db.backup

# Backup com data
cp precos.db precos.db.$(date +%Y%m%d_%H%M%S)
```

## 🔄 Fluxo de Dados

1. Usuário preenche formulário → `/api/contribuir`
2. API valida dados
3. Salva em `Produto` e `Preco` no SQLite
4. Commit permanente no arquivo `precos.db`
5. Busca retorna dados do banco

## 🚀 Tecnologias Usadas

- **SQLAlchemy**: ORM para gerenciar banco
- **SQLite**: Banco de dados arquivo
- **FastAPI**: API REST
- **Pydantic**: Validação de dados

## ⚠️ Importante

- O banco de dados é **persistente** e **não se perde**
- Cada contribuição tem timestamp único
- Dados podem ser exportados/importados
- Recomendado fazer backup periódico do arquivo `precos.db`
