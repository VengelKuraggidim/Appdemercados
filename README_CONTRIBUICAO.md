# 👥 Sistema de Contribuição Colaborativa

## 🎯 Como Funciona

Este sistema permite que **qualquer pessoa contribua** adicionando preços que encontrou em supermercados, criando uma **base de dados colaborativa** mantida pela comunidade!

## ✨ Funcionalidades Implementadas

### 1. ➕ Adicionar Preços
- Qualquer usuário pode cadastrar preços manualmente
- Campos: produto, marca, supermercado, preço, localização
- Indica se está em promoção
- Campo para observações (validade da promoção, etc)
- Opcional: nome do contribuidor

### 2. 👥 Ver Contribuições
- Lista todas as contribuições da comunidade
- Mostra quem contribuiu e quando
- Filtra por verificadas/não verificadas
- Ordenadas por data (mais recentes primeiro)

### 3. 📊 Estatísticas
- Total de contribuições
- Total de produtos cadastrados
- Total de supermercados
- Contribuições de hoje
- Última contribuição

### 4. 🔍 Buscar e Comparar
- Busca funciona com dados contribuídos
- Compara preços entre diferentes supermercados
- Mostra melhor preço e economia

## 🌐 URLs do Sistema

```
Frontend Principal: http://localhost:3000/
Adicionar Preço:    http://localhost:3000/contribuir.html
Ver Contribuições:  http://localhost:3000/contribuicoes.html
API:                http://localhost:8000
Documentação API:   http://localhost:8000/docs
```

## 📱 Como Usar

### Para Contribuir:

1. Acesse http://localhost:3000
2. Clique em "➕ Adicionar Preço"
3. Preencha o formulário:
   - Nome do produto (ex: "Arroz Tio João 5kg")
   - Marca (opcional)
   - Supermercado onde encontrou
   - Preço que viu
   - Se está em promoção
   - Sua localização (cidade/bairro)
   - Observações (ex: "Promoção válida até 31/10")
   - Seu nome (opcional)
4. Clique em "Enviar Contribuição"

### Para Ver Preços:

1. Acesse http://localhost:3000
2. Digite o produto que procura (ex: "arroz")
3. Veja os preços de diferentes supermercados
4. Compare e economize!

## 🔌 API Endpoints

### Contribuir com Preço
```bash
POST /api/contribuir
{
  "produto_nome": "Arroz Tio João 5kg",
  "produto_marca": "Tio João",
  "supermercado": "Carrefour",
  "preco": 22.90,
  "em_promocao": true,
  "localizacao": "São Paulo - Centro",
  "observacao": "Promoção válida até 31/10",
  "usuario_nome": "João Silva"
}
```

### Listar Contribuições
```bash
GET /api/contribuicoes?limit=50
```

### Estatísticas
```bash
GET /api/estatisticas-contribuicoes
```

### Supermercados Contribuídos
```bash
GET /api/supermercados-contribuidos
```

## 🎮 Testando o Sistema

### 1. Popular com dados de exemplo:
```bash
python popular_contribuicoes.py
```

### 2. Adicionar uma contribuição via API:
```bash
curl -X POST http://localhost:8000/api/contribuir \
  -H "Content-Type: application/json" \
  -d '{
    "produto_nome": "Feijão Preto 1kg",
    "supermercado": "Extra",
    "preco": 8.50,
    "em_promocao": true,
    "localizacao": "Rio de Janeiro"
  }'
```

### 3. Ver estatísticas:
```bash
curl http://localhost:8000/api/estatisticas-contribuicoes
```

## 💡 Vantagens do Sistema Colaborativo

### ✅ Vantagens:
- **Dados Reais**: Preços reais de pessoas reais
- **Sempre Atualizado**: Comunidade mantém atualizado
- **Sem Bloqueios**: Não depende de scraping
- **Legal**: Sem violar termos de serviço
- **Qualquer Loja**: Funciona com qualquer supermercado
- **Local**: Preços específicos por cidade/bairro
- **Promoções Relâmpago**: Usuários compartilham ofertas em tempo real

### ⚠️ Desafios:
- Depende de contribuições dos usuários
- Pode ter dados desatualizados
- Requer moderação para evitar dados falsos

## 🚀 Melhorias Futuras

### Gamificação:
- [ ] Sistema de pontos por contribuição
- [ ] Badges para contribuidores ativos
- [ ] Ranking de top contribuidores
- [ ] Níveis (Bronze, Prata, Ouro)

### Validação:
- [ ] Fotos dos preços como prova
- [ ] Votação da comunidade (útil/não útil)
- [ ] Verificação por moderadores
- [ ] Sistema de reputação

### Notificações:
- [ ] Alertas quando alguém encontra preço baixo
- [ ] Notificações push no PWA
- [ ] Email com melhores ofertas da semana

### Social:
- [ ] Comentários nas contribuições
- [ ] Compartilhar ofertas nas redes sociais
- [ ] Criar listas de compras colaborativas
- [ ] Grupos por bairro/cidade

### OCR/Fotos:
- [ ] Upload de foto do preço
- [ ] OCR automático para extrair preço
- [ ] Fotos de panfletos de supermercado
- [ ] Validação via foto

## 📈 Modelo de Dados

### Preco (estendido para contribuições):
```python
{
    "id": int,
    "produto_id": int,
    "supermercado": str,  # Qualquer nome
    "preco": float,
    "em_promocao": bool,
    "manual": bool,  # Se foi contribuição manual
    "usuario_nome": str,  # Quem contribuiu
    "localizacao": str,  # Onde encontrou
    "observacao": str,  # Notas adicionais
    "foto_url": str,  # Foto do preço (futuro)
    "verificado": bool,  # Moderação
    "data_coleta": datetime
}
```

## 🤝 Como a Comunidade Pode Ajudar

1. **Contribuir com preços** que você vê no dia a dia
2. **Validar contribuições** de outros usuários
3. **Reportar preços incorretos**
4. **Compartilhar o app** com amigos
5. **Sugerir melhorias**

---

## 🎉 Resultado

Você agora tem um **sistema colaborativo** onde:
- ✅ Qualquer pessoa pode adicionar preços
- ✅ Todos podem ver e comparar preços
- ✅ Funciona com qualquer supermercado
- ✅ Não depende de scraping bloqueado
- ✅ Dados reais da comunidade
- ✅ Interface simples e intuitiva

**Comece a contribuir agora!** 🛒💰
