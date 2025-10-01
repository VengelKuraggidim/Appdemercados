# 🛒 Comparador de Preços

Sistema completo para comparar preços de produtos em diferentes supermercados brasileiros, com app mobile (PWA).

## 🚀 Funcionalidades

- ✅ **Busca em múltiplos supermercados** (Carrefour, Pão de Açúcar, Extra, Mercado Livre)
- ✅ **Comparação de preços** em tempo real
- ✅ **Histórico de preços** - acompanhe a variação ao longo do tempo
- ✅ **Alertas de preço** - seja notificado quando o preço cair
- ✅ **PWA (Progressive Web App)** - funciona como app nativo no Android/iOS
- ✅ **API REST** completa e documentada
- ✅ **Busca paralela** para resultados mais rápidos

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

### Iniciar o servidor

```bash
python main.py
```

O servidor estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Frontend**: Servir os arquivos da pasta `frontend/`

### Servir o Frontend

Para servir o frontend PWA, você pode usar qualquer servidor HTTP. Por exemplo:

```bash
# Opção 1: Python http.server
cd frontend
python -m http.server 3000

# Opção 2: npm http-server (instale com: npm install -g http-server)
cd frontend
http-server -p 3000
```

Acesse: http://localhost:3000

### Testar os Scrapers

```bash
python test_scraper.py "arroz"
# ou
python test_scraper.py
```

## 📱 Instalar como App Mobile

1. Abra o frontend no navegador do celular
2. No Chrome/Edge: Menu → "Adicionar à tela inicial"
3. No Safari (iOS): Compartilhar → "Adicionar à Tela de Início"

O app funcionará como um aplicativo nativo!

## 🔌 API Endpoints

### Buscar Produtos
```bash
POST /api/buscar
{
  "termo": "arroz",
  "supermercados": ["carrefour", "pao_acucar"]  # opcional
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
