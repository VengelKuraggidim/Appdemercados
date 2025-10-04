# 🛒 Comparador de Preços

Sistema completo para comparar preços de produtos em diferentes supermercados brasileiros, com app mobile (PWA).

## 🚀 Funcionalidades

- ✅ **Buscar preços** de produtos em vários supermercados
- ✅ **Contribuir manualmente** adicionando preços que você encontrou
- ✅ **Contribuir por foto** usando OCR para detectar preços automaticamente
- ✅ **Comparação de preços** entre diferentes estabelecimentos
- ✅ **Histórico de preços** e contribuições
- ✅ **Dados persistentes** - salvos permanentemente em banco SQLite
- ✅ **PWA (Progressive Web App)** - funciona como app nativo
- ✅ **API REST** completa e documentada
- 🪙 **Sistema de Criptomoeda (PreçoCoin)** - Ganhe tokens contribuindo!

## 📦 Supermercados Suportados

- 🛒 **Carrefour**
- 🛒 **Pão de Açúcar**
- 🛒 **Extra**
- 🛒 **Mercado Livre**

## 🛠️ Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **BeautifulSoup** - Web scraping
- **APScheduler** - Agendamento de tarefas

### Frontend (PWA)
- **HTML5/CSS3/JavaScript** - Interface responsiva
- **Service Worker** - Funcionalidade offline
- **Progressive Web App** - Instalável em dispositivos móveis

## 📥 Instalação

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd PythonProject4
```

### 2. Crie um ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o ambiente (opcional)
```bash
cp .env.example .env
# Edite .env se necessário
```

## 🚀 Como Usar

### ⚡ Forma Rápida (Recomendado)

```bash
# Iniciar o app completo
./start_app.sh
```

O app estará disponível em: **http://localhost:8080**

Para parar:
```bash
./stop_app.sh
```

### 📝 Forma Manual

#### Iniciar Backend (API)
```bash
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

#### Iniciar Frontend
```bash
cd frontend
python -m http.server 8080
```

O servidor estará disponível em:
- **Frontend**: http://localhost:8080
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

## 💾 Persistência de Dados

**Importante:** Todos os dados são salvos permanentemente no banco de dados `precos.db`

- ✅ **Independente do navegador** - Dados não dependem de cache ou cookies
- ✅ **Permanente** - Dados permanecem mesmo após fechar o app
- ✅ **Portável** - Arquivo `precos.db` pode ser copiado/backupado

### Verificar dados salvos

```bash
# Ver estatísticas do banco
python verificar_banco.py

# Testar persistência
python teste_persistencia.py

# Popular com produtos de exemplo
python popular_produtos_basicos.py
```

## 📱 Instalar como App Mobile

1. Abra o frontend no navegador do celular
2. No Chrome/Edge: Menu → "Adicionar à tela inicial"
3. No Safari (iOS): Compartilhar → "Adicionar à Tela de Início"

O app funcionará como um aplicativo nativo!

## 🪙 Sistema de Criptomoeda - PreçoCoin (PRC)

O app possui um sistema de economia baseado em tokens para incentivar contribuições!

### Como Funciona

#### 💰 Ganhe Tokens:
- **5 tokens** ao criar sua carteira (bônus de boas-vindas)
- **10 tokens** por cada preço que você adicionar ao app

#### 💸 Gaste Tokens:
- **1 token** por cada busca de produto que você fizer

### Vantagens do Sistema
- ✅ Incentiva usuários a contribuírem com preços
- ✅ Gamificação: quanto mais você contribui, mais você pode buscar
- ✅ Sistema justo: todos começam com tokens gratuitos
- ✅ Ranking de mineradores (maiores contribuidores)

### Endpoints de Carteira

#### Criar Carteira
```bash
POST /api/carteira/criar
{
  "usuario_nome": "seu_usuario"
}
```

#### Consultar Saldo
```bash
GET /api/carteira/{usuario_nome}

# Resposta:
{
  "usuario_nome": "seu_usuario",
  "saldo": 15.0,
  "total_minerado": 20.0,
  "total_gasto": 5.0,
  "ultima_atualizacao": "2024-01-01T10:00:00"
}
```

#### Histórico de Transações
```bash
GET /api/carteira/{usuario_nome}/historico?limite=50
```

#### Verificar Saldo para Busca
```bash
GET /api/carteira/{usuario_nome}/pode-buscar
```

#### Informações do Sistema
```bash
GET /api/economia-token/info
```

#### Ranking de Mineradores
```bash
GET /api/ranking-mineradores?limite=10
```

## 🔌 API Endpoints

### Buscar Produtos (Custa 1 Token)
```bash
POST /api/buscar?usuario_nome=seu_usuario
{
  "termo": "arroz",
  "supermercados": ["carrefour", "pao_acucar"]  # opcional
}

# Resposta inclui informação de tokens:
{
  "termo": "arroz",
  "total": 10,
  "produtos": [...],
  "tokens": {
    "tokens_gastos": 1,
    "saldo_restante": 14
  }
}
```

### Comparar Preços
```bash
GET /api/comparar/{produto_nome}
```

### Listar Produtos
```bash
GET /api/produtos?skip=0&limit=50
```

### Histórico de Preços
```bash
GET /api/produtos/{produto_id}/historico?dias=7
```

### Criar Alerta
```bash
POST /api/alertas
{
  "produto_id": 1,
  "preco_alvo": 10.50,
  "email": "seu@email.com"
}
```

### Melhores Ofertas
```bash
GET /api/melhores-ofertas?limite=10
```

### Listar Supermercados
```bash
GET /api/supermercados
```

## 📊 Estrutura do Projeto

```
PythonProject4/
├── app/
│   ├── api/
│   │   └── main.py           # API FastAPI
│   ├── models/
│   │   ├── database.py       # Modelos do banco
│   │   └── schemas.py        # Schemas Pydantic
│   ├── scrapers/
│   │   ├── base.py           # Base scraper
│   │   ├── carrefour.py      # Scraper Carrefour
│   │   ├── pao_acucar.py     # Scraper Pão de Açúcar
│   │   ├── extra.py          # Scraper Extra
│   │   ├── mercado_livre.py  # Scraper Mercado Livre
│   │   └── scraper_manager.py # Gerenciador
│   └── utils/
│       ├── alertas.py        # Sistema de alertas
│       ├── comparador.py     # Lógica de comparação
│       └── scheduler.py      # Agendador de tarefas
├── frontend/
│   ├── index.html            # Interface principal
│   ├── manifest.json         # Manifesto PWA
│   ├── sw.js                 # Service Worker
│   └── src/
│       └── app.js            # Lógica do frontend
├── main.py                   # Entry point
├── test_scraper.py           # Script de teste
├── requirements.txt          # Dependências
└── README.md                 # Este arquivo
```

## ⚠️ Avisos Importantes

### Web Scraping
- Os scrapers podem parar de funcionar se os sites mudarem sua estrutura
- Respeite os termos de serviço dos sites
- Use delays entre requisições (já implementado)
- Alguns sites podem bloquear requisições automatizadas

### Recomendações
- Para uso em produção, considere usar APIs oficiais dos supermercados quando disponíveis
- Implemente cache para reduzir requisições
- Use um proxy rotativo para evitar bloqueios
- Considere usar Playwright/Selenium para sites com JavaScript pesado

## 🔧 Melhorias Futuras

- [ ] Adicionar mais supermercados
- [ ] Implementar notificações por email
- [ ] Sistema de lista de compras
- [ ] Otimização de rota de compras
- [ ] Análise de tendências de preços
- [ ] Modo escuro
- [ ] Autenticação de usuários
- [ ] Exportar comparações em PDF
- [x] **Sistema de criptomoeda para gamificação** ✅
- [ ] Transferência de tokens entre usuários
- [ ] Marketplace de tokens
- [ ] Recompensas especiais para top contribuidores

## 📄 Licença

MIT License - sinta-se livre para usar e modificar!

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
1. Fazer fork do projeto
2. Criar uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abrir um Pull Request

## 📞 Suporte

Se encontrar problemas:
1. Verifique se todas as dependências estão instaladas
2. Confira se o servidor está rodando
3. Veja os logs para identificar erros
4. Os sites podem ter mudado a estrutura (atualize os scrapers)

---

**Desenvolvido com ❤️ para economizar nas compras!** 🛒💰
# Appdemercados
