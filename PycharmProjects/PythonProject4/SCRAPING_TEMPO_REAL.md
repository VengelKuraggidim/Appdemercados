# 🔍 Sistema de Scraping em Tempo Real

## O que é?

Sistema inteligente que **busca preços REAIS de supermercados** quando o usuário faz uma pesquisa, mantendo o banco de dados sempre atualizado automaticamente.

## Como Funciona

### Fluxo de Busca

```
Usuário busca "arroz"
    ↓
Sistema tenta buscar preços REAIS nos supermercados
    ↓
    ├─ ✅ Encontrou preços → Salva no banco + Mostra para usuário
    │
    └─ ❌ Sites bloquearam → Mostra dados do banco
```

### Fontes de Dados

1. **Mercado Livre** - Tentativa via scraping direto
2. **Carrefour** - Tentativa via API interna (GraphQL)
3. **Extra/Pão de Açúcar** - Tentativa via API REST
4. **Contribuições de Usuários** - Sempre disponível ✅

## Implementação

### Arquivos Criados

- **`app/scrapers/scraper_tempo_real.py`** - Scraper otimizado para busca sob demanda
- **`app/api/main.py`** - Endpoint `/api/buscar` modificado para scraping em tempo real

### Código Principal

```python
# Quando usuário busca, sistema automaticamente tenta scraping
produtos_scraped = scraper_tempo_real.buscar_todos(request.termo, max_por_fonte=10)

# Salva novos preços no banco
for item in produtos_scraped:
    preco = Preco(
        produto_id=produto.id,
        supermercado=item['supermercado'],
        preco=item['preco'],
        data_coleta=datetime.now(),
        manual=False  # Automático
    )
    db.add(preco)
```

## Por que Sites Bloqueiam?

### Não é Ilegal!

- ✅ **Preços são públicos** - Qualquer pessoa pode ver
- ✅ **Não é crime** - Termos de uso ≠ Lei
- ⚠️  **Proteções técnicas** - Sites não querem sobrecarga nos servidores

### Proteções Comuns

1. **Cloudflare** - Detecta bots e bloqueia
2. **Rate Limiting** - Limita requisições por IP
3. **CAPTCHA** - Requer interação humana
4. **JavaScript pesado** - Dificulta scraping

## Vantagens do Sistema

### 1. Scraping Sob Demanda

✅ **Eficiente** - Só busca quando usuário precisa
✅ **Menos bloqueios** - Poucas requisições espalhadas
✅ **Dados atualizados** - Preços do momento da busca

### 2. Sistema Híbrido

```
Scraping Automático + Contribuições Manuais = Dados Sempre Disponíveis
```

### 3. Fallback Inteligente

- Sites bloquearam? → Mostra dados do banco
- Banco vazio? → Incentiva usuário a contribuir
- Contribuição manual → Ganha tokens 🪙

## Limitações Atuais

### Sites Bloqueando

Atualmente os sites estão bloqueando a maioria das tentativas:

```
🔍 Mercado Livre: 0 produtos (bloqueado)
🔍 Carrefour: 0 produtos (API requer auth)
🔍 Extra: 0 produtos (bloqueado)
```

### Por que ainda vale a pena?

1. **Sistema está pronto** - Quando sites mudarem proteções, já funciona
2. **Tentativa automática** - Não custa nada tentar
3. **Crowdsourcing funciona** - Usuários contribuem
4. **Alguns sites podem funcionar** - Depende do momento/IP

## Melhorias Futuras

### Opção 1: Proxies Rotativos 🔄

```python
# Usar proxies diferentes para cada requisição
proxies = ['proxy1', 'proxy2', 'proxy3']
response = requests.get(url, proxies=random.choice(proxies))
```

**Custo**: Proxies premium custam ~$50-200/mês

### Opção 2: Serviços Profissionais 💳

- **ScraperAPI** - $49/mês (1M requisições)
- **Bright Data** - $500/mês (ilimitado)
- **Oxylabs** - Preço sob consulta

### Opção 3: Parcerias Comerciais 🤝

- APIs oficiais de supermercados
- Integração com Rappi, iFood, Cornershop
- Requer negociação comercial

### Opção 4: Fortalecer Crowdsourcing 👥 (ATUAL)

✅ **Implementado**
✅ **Funciona bem**
✅ **Dados reais de usuários**
✅ **Gamificação com tokens**

## Testes

### Testar Scraper Diretamente

```bash
python3 testar_busca_tempo_real.py
```

### Testar via API

```bash
curl -X POST http://localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{"termo": "arroz"}'
```

### Verificar Logs

```bash
# Ver tentativas de scraping em tempo real
tail -f /tmp/uvicorn_app.log | grep "Buscando preços REAIS"
```

## Status Atual

✅ **Sistema implementado e funcionando**
⚠️  **Sites bloqueando scraping (esperado)**
✅ **Fallback para crowdsourcing funciona perfeitamente**
✅ **Usuários podem adicionar preços manualmente**

## Conclusão

O sistema de scraping em tempo real está **pronto e integrado**, mas devido às proteções dos sites, a melhor fonte de dados atualmente é o **crowdsourcing** (contribuições de usuários).

### Recomendação

Continue focando em:
1. ✅ Gamificação (tokens, reputação)
2. ✅ Sistema de validação comunitária
3. ✅ Incentivos para contribuição
4. 🔄 Monitorar se sites ficam mais acessíveis

---

**Criado em**: 2025-10-08
**Versão**: 1.0
**Status**: ✅ Implementado
