# 🔍 Soluções para Obter Preços Reais

O scraping direto de sites é bloqueado por proteções anti-bot. Aqui estão as **melhores alternativas**:

## ✅ Opção 1: APIs de Comparação de Preços (RECOMENDADO)

### A) Buscapé API
- Site: https://developer.buscape.com.br/
- ✅ API oficial com dados de milhares de lojas
- ✅ Preços atualizados
- ✅ Legal e confiável
- ⚠️ Pode ter custo após limite gratuito

### B) Zoom API
- Site: https://www.zoom.com.br/
- ✅ Comparador brasileiro popular
- ✅ Inclui supermercados
- ⚠️ Verifique disponibilidade de API

### C) Google Shopping API
- Site: https://developers.google.com/shopping-content
- ✅ Dados oficiais do Google Shopping
- ⚠️ Requer aprovação do Google
- ⚠️ Pode ter custos

## ✅ Opção 2: Serviços de Scraping (MAIS FÁCIL)

### A) SerpAPI (Recomendado)
```python
# pip install google-search-results
from serpapi import GoogleSearch

params = {
    "q": "arroz 5kg preço",
    "location": "Brazil",
    "hl": "pt-br",
    "gl": "br",
    "google_domain": "google.com.br",
    "api_key": "SUA_CHAVE_AQUI"
}

search = GoogleSearch(params)
results = search.get_dict()
```

- Site: https://serpapi.com/
- ✅ 100 buscas grátis/mês
- ✅ Retorna dados estruturados do Google
- ✅ Fácil de usar
- 💰 Plano pago após limite

### B) ScraperAPI
```python
import requests

url = "https://www.google.com/search?q=arroz+preço"
payload = {'api_key': 'SUA_CHAVE', 'url': url}
r = requests.get('http://api.scraperapi.com', params=payload)
```

- Site: https://www.scraperapi.com/
- ✅ 1000 requisições grátis/mês
- ✅ Contorna bloqueios automaticamente
- 💰 Plano pago após limite

## ✅ Opção 3: Playwright/Selenium com Stealth (Técnico)

```bash
pip install playwright
playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.google.com/search?q=arroz+preço")
    content = page.content()
    browser.close()
```

- ✅ Usa navegador real
- ✅ Menos chance de bloqueio
- ⚠️ Mais lento
- ⚠️ Mais recursos de CPU/RAM

## ✅ Opção 4: Dados Manuais + Crowdsourcing

1. **Usuários cadastram preços**
   - App permite tirar foto do preço
   - Comunidade contribui
   - Gamificação (pontos, badges)

2. **OCR em fotos de panfletos**
   - Usuários enviam fotos de folhetos
   - Extração automática com Tesseract/OCR

## 🚀 IMPLEMENTAÇÃO RECOMENDADA

### Para Desenvolvimento/Teste:
- Use **dados de demonstração** (já implementado)
- Usuários podem cadastrar preços manualmente

### Para Produção:
1. **Curto prazo**: Use **SerpAPI** (100 buscas grátis/mês)
2. **Médio prazo**: Integre **API do Buscapé**
3. **Longo prazo**: Sistema de crowdsourcing + scraping controlado

## 📝 Como Implementar SerpAPI (Rápido)

1. Criar conta: https://serpapi.com/users/sign_up
2. Pegar API key grátis
3. Instalar: `pip install google-search-results`
4. Usar no código:

```python
# app/scrapers/serpapi_scraper.py
from serpapi import GoogleSearch
import os

def buscar_precos(termo: str):
    params = {
        "q": f"{termo} preço comprar",
        "location": "Brazil",
        "hl": "pt-br",
        "gl": "br",
        "api_key": os.getenv("SERPAPI_KEY"),
        "num": 20
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    produtos = []
    for result in results.get("organic_results", []):
        # Processar resultados
        pass

    return produtos
```

## ⚠️ Importante

- **Web scraping agressivo pode violar termos de serviço**
- **Use delays entre requisições**
- **Respeite robots.txt**
- **Considere usar APIs oficiais quando possível**

---

**Qual opção você prefere implementar?**
