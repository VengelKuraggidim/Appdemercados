# 🔄 Sistema de Atualização Automática de Preços

Sistema completo para manter os preços sempre atualizados automaticamente.

## 📋 Como Funciona

### 1. **Script de Atualização Manual**
`atualizar_precos.py` - Executa busca e atualização de preços

**Modos disponíveis:**
- `--modo produtos` - Atualiza produtos existentes desatualizados
- `--modo basicos` - Busca e atualiza produtos básicos (arroz, feijão, etc.)
- `--modo ambos` - Executa ambas as atualizações (padrão)

**Uso:**
```bash
python3 atualizar_precos.py
python3 atualizar_precos.py --modo basicos
python3 atualizar_precos.py --modo produtos
```

### 2. **Agendador Automático**
`agendador_precos.py` - Agenda e executa atualizações periodicamente

**Frequência:**
- 🌅 **Atualização Completa**: Diariamente às 6h e 18h
- ⚡ **Atualização Rápida**: A cada 4 horas

**Uso:**
```bash
# Iniciar agendador
python3 agendador_precos.py

# Iniciar e executar imediatamente
python3 agendador_precos.py --executar-agora
```

### 3. **Iniciar App com Agendador**
`iniciar_com_agendador.sh` - Inicia tudo junto (API + Frontend + Agendador)

```bash
./iniciar_com_agendador.sh
```

## 🚀 Como Usar

### Opção 1: App sem agendador (manual)
```bash
./start_app.sh
```

### Opção 2: App com atualização automática (recomendado)
```bash
./iniciar_com_agendador.sh
```

### Parar tudo
```bash
./stop_app.sh
```

## 📝 Logs

Os logs são salvos em `logs/`:
- `api.log` - Log da API
- `frontend.log` - Log do frontend
- `agendador.log` - Log das atualizações automáticas

**Visualizar logs em tempo real:**
```bash
tail -f logs/agendador.log
tail -f logs/api.log
```

## ⚠️ Importante

**Limitação do Scraping:**
O Google Shopping pode bloquear requisições automatizadas. Se isso acontecer:

1. **Use contribuições manuais** - Sistema de tokens incentiva usuários a adicionar preços
2. **Configure proxies/VPN** - Para contornar bloqueios (avançado)
3. **Ajuste frequência** - Diminua a frequência das atualizações

## 🔧 Configurações Avançadas

### Alterar frequência do agendador
Edite `agendador_precos.py`:

```python
# Atualização completa
scheduler.add_job(
    executar_atualizacao_completa,
    CronTrigger(hour='6,18', minute=0),  # Altere aqui
    ...
)

# Atualização rápida
scheduler.add_job(
    executar_atualizacao_rapida,
    CronTrigger(hour='*/4'),  # A cada 4h - altere aqui
    ...
)
```

### Adicionar mais produtos básicos
Edite `atualizar_precos.py`:

```python
produtos_basicos = [
    "arroz",
    "feijão",
    # ... adicione mais aqui
]
```

## 💡 Dicas

1. **Contribuições são mais confiáveis**: Incentive usuários a adicionar preços via app
2. **Monitore os logs**: Verifique regularmente se as atualizações estão funcionando
3. **Combine métodos**: Use scraping + contribuições para melhor cobertura
4. **Sistema de tokens**: Já está configurado para recompensar contribuições

## 🎯 Próximos Passos

- [ ] Implementar API de supermercados (se disponível)
- [ ] Adicionar notificações quando scraping falhar
- [ ] Dashboard de monitoramento das atualizações
- [ ] Integração com webhook para alertas
