# Sistema de Atualização Automática de Preços

## Visão Geral

O sistema de atualização automática de preços foi implementado para manter os preços dos produtos sempre atualizados no banco de dados. Ele executa buscas periódicas nos supermercados cadastrados e atualiza os preços automaticamente.

## Características

- **Frequência**: Atualização a cada 7 horas
- **Logging**: Logs detalhados salvos em `logs/atualizacao_precos.log` e `logs/agendador_precos.log`
- **Integrado**: Inicia automaticamente com a aplicação FastAPI
- **Inteligente**: Atualiza apenas produtos com preços desatualizados (mais de 24h)

## Como Funciona

### Integração Automática

O sistema inicia automaticamente quando você roda a aplicação FastAPI:

```bash
uvicorn app.api.main:app --reload
```

O agendador é iniciado em background e executará a atualização a cada 7 horas automaticamente.

### Arquivos Principais

1. **`app/utils/price_updater.py`**
   - Módulo principal do agendador
   - Contém a classe `PriceUpdater`
   - Integrado à aplicação FastAPI

2. **`atualizar_precos.py`**
   - Script standalone para atualização manual
   - Pode ser executado independentemente

3. **`agendador_precos.py`**
   - Script standalone do agendador
   - Útil para rodar o agendador separadamente da API

4. **`test_agendador_precos.py`**
   - Script de teste do agendador
   - Verifica se tudo está funcionando corretamente

## Uso Manual

### Atualizar Preços Manualmente

```bash
# Atualizar produtos existentes e básicos
python3 atualizar_precos.py

# Atualizar apenas produtos existentes
python3 atualizar_precos.py --modo produtos

# Atualizar apenas produtos básicos
python3 atualizar_precos.py --modo basicos
```

### Rodar Agendador Standalone

```bash
# Iniciar agendador (a cada 7 horas)
python3 agendador_precos.py

# Iniciar e executar atualização imediatamente
python3 agendador_precos.py --executar-agora
```

### Testar o Sistema

```bash
python3 test_agendador_precos.py
```

## Logs

Os logs são salvos em:
- `logs/atualizacao_precos.log` - Logs das atualizações de preços
- `logs/agendador_precos.log` - Logs do agendador

Exemplo de log:
```
2025-10-08 20:24:59,204 - INFO - 🔄 Iniciando atualização automática de preços
2025-10-08 20:24:59,250 - INFO - 📦 Encontrados 15 produtos para atualizar
2025-10-08 20:24:59,300 - INFO - ✅ Produtos atualizados: 15
2025-10-08 20:24:59,300 - INFO - ✅ Novos preços adicionados: 45
```

## Configuração

### Alterar Intervalo de Atualização

Para alterar o intervalo de atualização, modifique em `app/api/main.py`:

```python
# Padrão: a cada 7 horas
price_updater.start(interval_hours=7)

# Exemplo: a cada 4 horas
price_updater.start(interval_hours=4)

# Exemplo: a cada 12 horas
price_updater.start(interval_hours=12)
```

### Modificar Produtos a Atualizar

Em `atualizar_precos.py`, você pode modificar:

1. **Número de produtos atualizados**:
```python
# Linha 44: Altere .limit(20) para mais ou menos produtos
produtos = db.query(Produto).join(Preco).filter(
    Preco.data_coleta < data_limite
).group_by(Produto.id).limit(20).all()  # <- Altere aqui
```

2. **Tempo de desatualização**:
```python
# Linha 40: Altere timedelta(hours=24) para mais ou menos horas
data_limite = datetime.now() - timedelta(hours=24)  # <- Altere aqui
```

3. **Lista de produtos básicos**:
```python
# Linha 118-127: Adicione ou remova produtos
produtos_basicos = [
    "arroz",
    "feijão",
    "açúcar",
    # ... adicione mais produtos aqui
]
```

## Requisitos

- Python 3.7+
- APScheduler 3.11.0+
- SQLAlchemy
- FastAPI

## Troubleshooting

### O agendador não está rodando

1. Verifique se a aplicação FastAPI está rodando
2. Confira os logs em `logs/agendador_precos.log`
3. Execute o teste: `python3 test_agendador_precos.py`

### Nenhum produto sendo atualizado

Isso pode acontecer se:
- Todos os produtos têm preços recentes (menos de 24h)
- Não há produtos no banco de dados
- Os scrapers estão falhando (verifique os logs)

### Scrapers falhando

Os scrapers podem falhar devido a:
- Mudanças nos sites dos supermercados
- Bloqueio por IP (Google Shopping)
- Problemas de rede

Verifique os logs para mais detalhes.

## Próximos Passos

Sugestões de melhorias futuras:
- [ ] Adicionar suporte a mais supermercados
- [ ] Implementar cache de requisições
- [ ] Adicionar notificações de falhas
- [ ] Dashboard de monitoramento
- [ ] Métricas de atualização (Prometheus/Grafana)
- [ ] Retry automático em caso de falha

## Suporte

Para problemas ou sugestões, abra uma issue no repositório.
