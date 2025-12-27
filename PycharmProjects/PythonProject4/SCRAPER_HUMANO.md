# 🤖 Scraper Humano - Sistema Anti-Detecção

## 📋 Visão Geral

O **Scraper Humano** é uma solução avançada de web scraping que imita comportamento humano para evitar detecção e bloqueio por sites de supermercados.

### ✨ Diferenciais

1. **Anti-Detecção Avançada**
   - Usa `undetected-chromedriver` que evita detecção automática
   - Remove propriedades JavaScript que indicam automação
   - User-agent realista e headers customizados

2. **Comportamento Humano**
   - Delays aleatórios entre ações (2-5 segundos)
   - Scroll suave e aleatório pela página
   - Movimentação de mouse simulada
   - Tempo de espera variável

3. **Robustez**
   - Múltiplos seletores CSS para cada elemento
   - Fallbacks automáticos se um seletor falhar
   - Tratamento de erros em cada produto individualmente
   - Scroll até elemento antes de extrair dados

4. **Integração Inteligente**
   - Integrado com o sistema existente
   - Usado como fallback quando APIs falham
   - Ativa automaticamente quando poucos produtos são encontrados

## 🚀 Como Usar

### 1. Uso Direto

```python
from app.scrapers.scraper_humano import ScraperHumano

# Criar scraper
scraper = ScraperHumano(headless=True)  # headless=False para ver o navegador

# Buscar em um mercado específico
produtos = scraper.buscar_carrefour("arroz")
produtos = scraper.buscar_pao_acucar("feijão")
produtos = scraper.buscar_extra("café")

# Buscar em todos os mercados
produtos = scraper.buscar_todos("leite", mercados=['carrefour', 'pao_acucar'])

# Fechar quando terminar
scraper.close()
```

### 2. Uso via Instância Global (Recomendado)

```python
from app.scrapers.scraper_humano import get_scraper_humano

# Pega instância global (reutiliza sessão)
scraper = get_scraper_humano(headless=True)

produtos = scraper.buscar_todos("chocolate")

# Não precisa fechar - a instância fica ativa
```

### 3. Integração Automática

O scraper humano está **integrado automaticamente** no sistema de busca em tempo real:

```python
from app.scrapers.scraper_tempo_real import scraper_tempo_real

# Quando você faz uma busca, o sistema:
# 1. Tenta APIs rápidas primeiro (Mercado Livre, Carrefour, Extra)
# 2. Se encontrar < 5 produtos, ativa o Scraper Humano automaticamente
produtos = scraper_tempo_real.buscar_todos("arroz", usar_selenium=True)
```

## 📊 Formato dos Dados

Cada produto retornado tem a estrutura:

```python
{
    'nome': 'Arroz Tio João 5kg',
    'marca': None,  # Extraído quando disponível
    'preco': 25.90,
    'preco_original': 29.90,  # Se em promoção
    'em_promocao': True,
    'url': 'https://...',
    'supermercado': 'Carrefour',
    'disponivel': True
}
```

## 🧪 Testes

### Teste Rápido
```bash
python teste_rapido_scraper.py
```

### Teste Completo Interativo
```bash
python testar_scraper_humano.py
```

O teste completo permite:
- Escolher o produto para buscar
- Selecionar mercados específicos
- Ver o navegador funcionando (headless=False)
- Exportar resultados em JSON

## ⚙️ Configuração

### Modo Headless vs Visual

**Headless (Padrão - Produção)**
```python
scraper = ScraperHumano(headless=True)
```
- Mais rápido
- Usa menos recursos
- Ideal para produção

**Visual (Desenvolvimento/Debug)**
```python
scraper = ScraperHumano(headless=False)
```
- Você vê o navegador
- Útil para debug
- Permite ver exatamente o que está acontecendo

### Tempos de Espera

Você pode customizar os tempos de espera:

```python
scraper = ScraperHumano()
scraper.wait_time = (1, 3)  # Mínimo 1s, máximo 3s (mais rápido)
scraper.wait_time = (3, 7)  # Mínimo 3s, máximo 7s (mais humano)
```

## 🔧 Troubleshooting

### "Nenhum produto encontrado"

**Possíveis causas:**
1. **Seletores CSS mudaram** - Sites mudam sua estrutura
   - Solução: Atualizar seletores em `scraper_humano.py`

2. **Site detectou bot**
   - Solução: Aumentar delays, usar headless=False temporariamente

3. **Produto realmente não existe**
   - Teste com termo genérico como "arroz"

### Chrome não encontrado

```bash
# Ubuntu/Debian
sudo apt-get install chromium-browser

# ou Chrome completo
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### Erro de permissão

```bash
# Dar permissão ao ChromeDriver
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver
```

## 📈 Performance

### Velocidade Média por Mercado
- Carrefour: 15-25 segundos
- Pão de Açúcar: 15-25 segundos
- Extra: 15-25 segundos

### Otimizações
- Usa instância global para reutilizar sessão
- Processa apenas os 15 primeiros produtos
- Scroll inteligente (não carrega página inteira)

## 🔒 Boas Práticas

### ✅ Fazer

1. **Usar delays realistas**
   ```python
   scraper.wait_time = (2, 5)  # Bom
   ```

2. **Reutilizar instância**
   ```python
   scraper = get_scraper_humano()  # Reusa sessão
   ```

3. **Fechar quando não usar mais**
   ```python
   scraper.close()
   ```

### ❌ Não Fazer

1. **Fazer muitas requisições rápidas**
   ```python
   # RUIM - Vai ser bloqueado
   for termo in ['arroz', 'feijão', 'café']:
       scraper.buscar_carrefour(termo)
   ```

2. **Usar delays muito curtos**
   ```python
   scraper.wait_time = (0.1, 0.2)  # Vai ser detectado!
   ```

3. **Criar muitas instâncias**
   ```python
   # RUIM - Consome muita memória
   for i in range(100):
       s = ScraperHumano()
   ```

## 🚦 Status de Mercados

| Mercado | Status | Observações |
|---------|--------|-------------|
| Carrefour | ✅ Funcionando | Estrutura estável |
| Pão de Açúcar | ✅ Funcionando | Mesmo grupo do Extra |
| Extra | ✅ Funcionando | Similar ao Pão de Açúcar |
| Mercado Livre | ⚠️ API Simples | Não usa Selenium |

## 📝 Logs

O scraper emite logs úteis:

```
🔍 Acessando Carrefour: arroz
✓ Encontrados 24 produtos
✅ Carrefour: 15 produtos extraídos
```

Símbolos:
- 🔍 = Iniciando busca
- ✓ = Produtos encontrados na página
- ✅ = Extração bem-sucedida
- ⚠️ = Aviso (poucos produtos)
- ❌ = Erro

## 🔄 Atualizações Futuras

Planejado:
- [ ] Suporte a mais supermercados (Walmart, Mercadinho, etc)
- [ ] Extração de imagens dos produtos
- [ ] Cache inteligente de resultados
- [ ] Busca paralela em múltiplos mercados
- [ ] Detecção automática de mudanças em seletores
- [ ] Rotação de User-Agents
- [ ] Suporte a proxy

## 💡 Dicas

1. **Para desenvolvimento**: Use `headless=False` para ver o que está acontecendo
2. **Para produção**: Use `headless=True` e instância global
3. **Se bloqueado**: Aumente os delays e adicione mais comportamento humano
4. **Performance**: Limite os mercados buscados ao necessário
5. **Debug**: Verifique os logs para entender onde está falhando

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs
2. Teste com `headless=False` para debug visual
3. Confirme que Chrome está instalado
4. Verifique se os seletores CSS ainda são válidos
5. Aumente os delays se suspeitar de bloqueio

---

**Versão**: 1.0.0
**Última Atualização**: 2025-10-31
**Compatibilidade**: Python 3.8+, Selenium 4.15+, undetected-chromedriver 3.5+
