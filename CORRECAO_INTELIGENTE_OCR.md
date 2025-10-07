# 🤖 Correção Inteligente de OCR

## O que é?

Sistema automático de correção de erros de OCR usando **Inteligência Artificial de Similaridade**.

Quando a foto da nota fiscal está com baixa qualidade (comum em fotos do WhatsApp), o OCR pode ler palavras erradas.

Nosso sistema **automaticamente corrige** essas palavras comparando com um dicionário de produtos comuns de supermercado.

---

## Como funciona?

### 1. **Algoritmo de Similaridade (Levenshtein)**

Comparamos cada palavra extraída com um dicionário de 100+ produtos usando o algoritmo **SequenceMatcher** que calcula a similaridade entre strings.

### 2. **Threshold de 75%**

Só corrigimos se a similaridade for **≥ 75%** para evitar correções erradas.

### 3. **Correção palavra por palavra**

Em nomes compostos como "CARE COM LEILE", corrigimos cada palavra:
- CARE → CARNE (89% similar)
- COM → COM (sem correção)
- LEILE → LEITE (80% similar)

Resultado: **"CARNE COM LEITE"**

---

## Exemplos de Correção

| OCR Errado | Corrigido | Similaridade |
|------------|-----------|--------------|
| CARE | CARNE | 89% |
| NELAO | MELAO | 80% |
| RARINHA | FARINHA | 86% |
| LEILE | LEITE | 80% |
| BANAHA | BANANA | 83% |
| FRARGO | FRANGO | 83% |
| REFRIGERARTE | REFRIGERANTE | 92% |
| OLED | OLEO | 75% |

---

## Dicionário de Produtos

O sistema conhece **100+ produtos comuns** de supermercado brasileiro:

### Grãos e Cereais
ARROZ, FEIJÃO, MACARRÃO, FARINHA, FUBÁ, AVEIA, GRANOLA, QUINOA

### Bebidas
CAFÉ, CHÁ, SUCO, REFRIGERANTE, ÁGUA, CERVEJA, VINHO, LEITE, IOGURTE, ACHOCOLATADO

### Frutas e Verduras
BANANA, MAÇÃ, LARANJA, LIMÃO, MELÃO, MELANCIA, MAMÃO, MORANGO, UVA, PERA, ABACAXI, TOMATE, CEBOLA, ALHO, BATATA, CENOURA, ALFACE, REPOLHO, BRÓCOLIS, COUVE, PEPINO, PIMENTÃO

### Carnes e Proteínas
CARNE, FRANGO, PEIXE, LINGUIÇA, SALSICHA, BACON, PRESUNTO, MORTADELA, SALAME, OVO

### Laticínios
QUEIJO, MANTEIGA, MARGARINA, REQUEIJÃO, CREAM CHEESE

### Condimentos
SAL, PIMENTA, ÓLEO, AZEITE, VINAGRE, MOLHO, KETCHUP, MAIONESE, MOSTARDA

### Produtos de Limpeza
SABÃO, DETERGENTE, AMACIANTE, DESINFETANTE, ÁGUA SANITÁRIA, ALVEJANTE, ESPONJA, PAPEL HIGIÊNICO

### Higiene Pessoal
SHAMPOO, CONDICIONADOR, SABONETE, PASTA DE DENTE, DESODORANTE, ABSORVENTE

### Outros
AÇÚCAR, BISCOITO, BOLACHA, PÃO, BOLO, CHOCOLATE, SORVETE, PIRÃO, SARDINHA, ATUM

---

## Vantagens

✅ **Automático**: Não precisa de intervenção manual
✅ **Inteligente**: Usa algoritmo de similaridade comprovado
✅ **Preciso**: Só corrige se ≥ 75% de certeza
✅ **Rápido**: Processa em milissegundos
✅ **Extensível**: Fácil adicionar mais produtos ao dicionário

---

## Como testar?

Execute o script de teste:

```bash
python test_correcao_ocr.py
```

Ou envie uma foto de nota fiscal no **Debug OCR** e veja os logs no console:

```
🤖 CORREÇÃO OCR: 'CARE' -> 'CARNE' (similaridade: 89%)
🤖 CORREÇÃO OCR: 'NELAO' -> 'MELAO' (similaridade: 80%)
```

---

## Código

O código está em `app/utils/ocr_nota_fiscal.py`:

- `corrigir_nome_produto_com_ia()` - Corrige uma palavra
- `corrigir_palavras_no_nome()` - Corrige cada palavra em um nome composto

---

## Próximas Melhorias

- [ ] Adicionar mais produtos ao dicionário
- [ ] Usar LLM (GPT/Claude) para correções mais complexas
- [ ] Aprender com correções manuais dos usuários
- [ ] Detectar marcas e especificações

---

**Desenvolvido com ❤️ para melhorar a experiência de escaneamento de notas fiscais!**
