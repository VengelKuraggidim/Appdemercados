"""
Script de teste para demonstrar a correção inteligente de OCR
"""

from app.utils.ocr_nota_fiscal import NotaFiscalOCR

# Criar instância
ocr = NotaFiscalOCR()

# Exemplos de erros comuns de OCR
testes = [
    "CARE",           # -> CAFE
    "NELAO",          # -> MELAO
    "RARINHA",        # -> FARINHA
    "ACUCAR",         # -> AÇÚCAR
    "LEILE",          # -> LEITE
    "ARRCS",          # -> ARROZ
    "RELAO",          # -> MELAO
    "BANAHA",         # -> BANANA
    "CARE COM LEILE", # -> CAFE COM LEITE
    "RARINHA DE TRIGO", # -> FARINHA DE TRIGO
    "OLED",           # -> OLEO
    "CARNE BOUINA",   # -> CARNE (BOUINA não corrige)
    "FRARGO",         # -> FRANGO
    "REFRIGERARTE",   # -> REFRIGERANTE
]

print("=" * 80)
print("TESTE DE CORREÇÃO INTELIGENTE DE OCR")
print("=" * 80)
print()

for teste in testes:
    corrigido = ocr.corrigir_palavras_no_nome(teste)
    if teste != corrigido:
        print(f"✅ '{teste}' -> '{corrigido}'")
    else:
        print(f"⚪ '{teste}' (sem correção)")

print()
print("=" * 80)
print("COMO FUNCIONA:")
print("- Usa algoritmo de similaridade de strings (Levenshtein)")
print("- Compara com dicionário de 100+ produtos comuns")
print("- Apenas corrige se similaridade >= 75%")
print("- Corrige palavra por palavra em nomes compostos")
print("=" * 80)
