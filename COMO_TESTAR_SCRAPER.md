# 🧪 Como Testar o Scraper Humano

## 🚀 Guia Rápido de Teste

### Opção 1: Teste Rápido (Headless)

**Mais rápido, sem interface visual**

```bash
python teste_rapido_scraper.py
```

O que faz:
- Busca "arroz" no Carrefour
- Mostra os 3 primeiros resultados
- Roda em modo headless (sem abrir janela)

### Opção 2: Teste Completo (Visual)

**Ver o navegador funcionando**

```bash
python testar_scraper_humano.py
```

O que faz:
- Pergunta qual produto buscar
- Deixa você escolher os mercados
- Mostra o navegador funcionando
- Salva resultados em JSON
- Mostra estatísticas completas

### Opção 3: Teste via API

**Testar a integração com o sistema**

1. Inicie o servidor:
```bash
uvicorn app.api.main:app --reload
```

2. Faça uma busca via API:
```bash
curl -X POST "http://localhost:8000/api/buscar" \
  -H "Content-Type: application/json" \
  -d '{"termo": "arroz"}'
```

3. O sistema vai:
   - Tentar APIs rápidas primeiro
   - Se encontrar < 5 produtos, ativar Scraper Humano
   - Retornar todos os produtos encontrados

## 📋 Checklist de Teste

### ✅ Testes Básicos

- [ ] Instalar dependências
  ```bash
  pip install undetected-chromedriver webdriver-manager
  ```

- [ ] Verificar Chrome instalado
  ```bash
  google-chrome --version
  # ou
  chromium --version
  ```

- [ ] Teste rápido funciona
  ```bash
  python teste_rapido_scraper.py
  ```

- [ ] Produtos são retornados com preços válidos

### ✅ Testes Avançados

- [ ] Teste visual (ver navegador)
  - Editar `testar_scraper_humano.py`
  - Mudar `headless=False` na linha do ScraperHumano
  - Executar e observar comportamento

- [ ] Teste com diferentes produtos
  - "arroz"
  - "feijão"
  - "café"
  - "leite"
  - "chocolate"

- [ ] Teste em diferentes mercados
  - Carrefour
  - Pão de Açúcar
  - Extra

- [ ] Teste de integração
  - API /api/buscar retorna produtos
  - Produtos são salvos no banco
  - Frontend exibe corretamente

## 🐛 Debug

### Ver o navegador funcionando

Edite o arquivo que está usando e mude:

```python
# De:
scraper = ScraperHumano(headless=True)

# Para:
scraper = ScraperHumano(headless=False)
```

Agora você verá:
- O navegador abrindo
- Navegando até o site
- Scrollando pela página
- Extraindo dados

### Ver mais detalhes nos logs

Os logs já são bem verbosos, mas você pode adicionar:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspecionar HTML

Se quiser ver o HTML da página:

```python
from app.scrapers.scraper_humano import ScraperHumano

scraper = ScraperHumano(headless=False)
scraper._init_driver()
scraper.driver.get("https://mercado.carrefour.com.br/busca?q=arroz")

# Esperar carregar
import time
time.sleep(5)

# Ver HTML
print(scraper.driver.page_source)

# Ou salvar em arquivo
with open('debug.html', 'w') as f:
    f.write(scraper.driver.page_source)

scraper.close()
```

## 🔍 Problemas Comuns

### 1. "Chrome não encontrado"

**Solução**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install chromium-browser

# Ou instalar Chrome:
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

### 2. "Nenhum produto encontrado"

**Debug**:
```python
# 1. Teste com headless=False para ver o que está acontecendo
scraper = ScraperHumano(headless=False)

# 2. Veja se a página carrega corretamente
scraper._init_driver()
scraper.driver.get("https://mercado.carrefour.com.br/busca?q=arroz")
input("Pressione Enter depois de ver a página...")

# 3. Verifique os seletores
# Veja se os elementos estão na página com DevTools
```

**Possíveis causas**:
- Site mudou estrutura HTML → Atualizar seletores
- Site bloqueou → Aumentar delays
- Problema de rede → Verificar conexão
- Produto não existe → Testar com "arroz"

### 3. "Muito lento"

**Otimizações**:

```python
# Reduzir delays (CUIDADO: pode ser detectado)
scraper = ScraperHumano(headless=True)
scraper.wait_time = (1, 2)  # Mais rápido

# Buscar em menos mercados
produtos = scraper.buscar_todos("arroz", mercados=['carrefour'])

# Limitar produtos por mercado
produtos = scraper.buscar_carrefour("arroz")
produtos = produtos[:5]  # Apenas 5 primeiros
```

### 4. Erro "WebDriver" ou "ChromeDriver"

**Solução**:
```bash
# Atualizar webdriver-manager
pip install --upgrade webdriver-manager

# Limpar cache
rm -rf ~/.wdm

# Reinstalar
pip uninstall selenium webdriver-manager undetected-chromedriver
pip install selenium webdriver-manager undetected-chromedriver
```

## 📊 Interpretando Resultados

### Exemplo de saída bem-sucedida:

```
🔍 Acessando Carrefour: arroz
   ✓ Encontrados 24 produtos
   ✅ Carrefour: 15 produtos extraídos

🔍 Acessando Pão de Açúcar: arroz
   ✓ Encontrados 18 produtos
   ✅ Pão de Açúcar: 12 produtos extraídos

✅ TOTAL: 27 produtos únicos encontrados
```

**Indica**:
- ✅ Scraper funcionando
- ✅ Produtos sendo extraídos
- ✅ Sistema de deduplicação funcionando

### Exemplo de problema:

```
🔍 Acessando Carrefour: arroz
   ⚠️  Nenhum produto encontrado
```

**Indica**:
- ⚠️ Seletores podem estar desatualizados
- ⚠️ Ou site bloqueou
- ⚠️ Ou produto não existe

## 🎯 Testes de Validação

### Teste 1: Preços válidos
```python
produtos = scraper.buscar_carrefour("arroz")
assert all(p['preco'] > 0 for p in produtos), "Preços inválidos!"
print("✅ Todos os preços são válidos")
```

### Teste 2: Nomes não vazios
```python
produtos = scraper.buscar_carrefour("arroz")
assert all(len(p['nome']) > 3 for p in produtos), "Nomes muito curtos!"
print("✅ Todos os nomes são válidos")
```

### Teste 3: URLs corretas
```python
produtos = scraper.buscar_carrefour("arroz")
assert all(p['url'].startswith('http') for p in produtos if p['url']), "URLs inválidas!"
print("✅ Todas as URLs são válidas")
```

### Teste 4: Supermercado correto
```python
produtos = scraper.buscar_carrefour("arroz")
assert all(p['supermercado'] == 'Carrefour' for p in produtos), "Supermercado errado!"
print("✅ Supermercado correto")
```

## 📝 Script de Teste Completo

Crie `validar_scraper.py`:

```python
from app.scrapers.scraper_humano import ScraperHumano

def validar():
    print("🧪 Validando Scraper Humano\n")

    scraper = ScraperHumano(headless=True)

    try:
        # Teste 1: Buscar produtos
        print("1. Buscando produtos...")
        produtos = scraper.buscar_carrefour("arroz")
        assert len(produtos) > 0, "Nenhum produto encontrado!"
        print(f"   ✅ {len(produtos)} produtos encontrados")

        # Teste 2: Preços válidos
        print("2. Validando preços...")
        assert all(p['preco'] > 0 for p in produtos)
        print(f"   ✅ Preços válidos (R$ {min(p['preco'] for p in produtos):.2f} - R$ {max(p['preco'] for p in produtos):.2f})")

        # Teste 3: Nomes
        print("3. Validando nomes...")
        assert all(len(p['nome']) > 3 for p in produtos)
        print(f"   ✅ Nomes válidos")

        # Teste 4: Estrutura
        print("4. Validando estrutura...")
        campos = ['nome', 'preco', 'supermercado', 'disponivel']
        assert all(all(campo in p for campo in campos) for p in produtos)
        print(f"   ✅ Estrutura correta")

        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return True

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False

    finally:
        scraper.close()

if __name__ == "__main__":
    validar()
```

Execute:
```bash
python validar_scraper.py
```

## 💪 Próximos Passos

Após validar que funciona:

1. **Integrar com frontend**
   - Testar via interface web
   - Verificar exibição de produtos

2. **Testar em produção**
   - Monitorar logs
   - Verificar taxa de sucesso
   - Ajustar delays se necessário

3. **Otimizar**
   - Identificar gargalos
   - Melhorar seletores
   - Adicionar cache

4. **Monitorar**
   - Taxa de sucesso por mercado
   - Tempo médio de scraping
   - Produtos encontrados vs esperados

---

**Dica Final**: Sempre teste com `headless=False` primeiro para entender o que está acontecendo antes de colocar em produção com `headless=True`.
