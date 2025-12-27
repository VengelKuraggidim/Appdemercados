#!/usr/bin/env python3
"""
Teste com a nota fiscal real do usuário
"""

from app.utils.ocr_nota_fiscal import NotaFiscalOCR

# Texto REAL da nota fiscal do usuário
texto_nota_real = """
COMERCIO DE ALIMENTOS
LOJA DOS DESCONTOS
Rua Souza Melo, 1245 Maua
CNPJ:04.895.751/0001-74
1E:15.000.611-0
03/04/2013 15:31:48  CCF:001757 C00:004776
cupoM FISCAL
[IEM SÓLICO DESCRIÇÃO GAD.UN-VI. WMIT( R$) SE VE IT2M( R$)
002 21259005 — DESOD SANIT PINH-SANIFECI -356
21%1,09 717,00 2,086
002 57192502 "QUEIJO MUSSARELA GIROLANDA -KG
0,3 X 1749 727,00% 5,246
003 87224500 " BATATA PALHA SLI-MICOS "706
3x2,29 717,00% 6,876
004 57001707 "SOB LACTEA CREAM-BATAVO  -2005
2% 2,88 717,00% 2,986
005 57002401 "BL FERM POLPA MO-BATAVO  -5406
2% 3,08 717,008 3,096
006 57005400  x4BEBIDA LACTEA -PAULI -6006
1x2,43 717,00% 2,436
TOTAL R$ 21,71
Dinheiro an
IMPOSTOS Valor=R$7.22  Megia=33.35%
mM aroma ECRIF
| VERSÃO: 01.00.02 ECF:100 LJ:0001
| QRRNDOCOQWUUTTTIWYO 03/04/2013 15:32:01
FAB: IB030800000008200130 ar
"""

def testar():
    print("=" * 70)
    print("🔬 ANÁLISE DA SUA NOTA FISCAL")
    print("=" * 70)
    print()

    ocr = NotaFiscalOCR()

    # 1. Supermercado
    print("1️⃣ SUPERMERCADO:")
    supermercado = ocr.identificar_supermercado(texto_nota_real)
    if supermercado:
        print(f"   ✅ Identificado: {supermercado}")
    else:
        print("   ❌ NÃO IDENTIFICADO")
        print("   📝 Texto encontrado: 'LOJA DOS DESCONTOS'")
        print("   💡 Solução: Adicionar ao dicionário SUPERMERCADOS")
    print()

    # 2. Data
    print("2️⃣ DATA:")
    data = ocr.extrair_data(texto_nota_real)
    if data:
        print(f"   ✅ Encontrada: {data.strftime('%d/%m/%Y')}")
    else:
        print("   ❌ NÃO ENCONTRADA")
        print("   📝 Data no texto: '03/04/2013 15:31:48'")
        print("   💡 O padrão já deveria pegar isso...")
    print()

    # 3. Produtos
    print("3️⃣ PRODUTOS:")
    produtos = ocr.extrair_produtos(texto_nota_real)
    print(f"   Total encontrado: {len(produtos)} produtos")
    print(f"   Esperado: 6 produtos")
    print()

    if produtos:
        print("   Produtos extraídos:")
        for i, prod in enumerate(produtos, 1):
            print(f"   {i}. {prod['nome']:40} R$ {prod['preco']:7.2f} ({prod['quantidade']}x)")
    else:
        print("   ❌ NENHUM PRODUTO ENCONTRADO!")
        print()
        print("   📝 Formato das linhas de produto:")
        print("   002 21259005 — DESOD SANIT PINH-SANIFECI -356")
        print("   21%1,09 717,00 2,086")
        print()
        print("   ⚠️  PROBLEMA: Formato muito diferente do padrão!")
        print("   - Produto e preço estão em LINHAS SEPARADAS")
        print("   - Preço final está no final: '2,086'")
    print()

    # 4. Total
    print("4️⃣ TOTAL:")
    total = ocr.extrair_total(texto_nota_real)
    if total:
        print(f"   ✅ Encontrado: R$ {total:.2f}")
    else:
        print("   ❌ NÃO ENCONTRADO")
        print("   📝 Total no texto: 'TOTAL R$ 21,71'")
        print("   💡 Padrão já deveria pegar isso...")
    print()

    # 5. Análise detalhada
    print("=" * 70)
    print("📊 DIAGNÓSTICO:")
    print("=" * 70)
    print()

    print("🔍 PROBLEMAS IDENTIFICADOS:")
    print()

    print("1. FORMATO DA NOTA DIFERENTE:")
    print("   Esta nota tem um formato especial onde:")
    print("   - Nome do produto está em uma linha")
    print("   - Quantidade e preço estão na linha SEGUINTE")
    print()
    print("   Exemplo:")
    print("   002 57192502 'QUEIJO MUSSARELA GIROLANDA -KG")
    print("   0,3 X 1749 727,00% 5,246")
    print("                          ↑")
    print("                    Preço aqui!")
    print()

    print("2. SUPERMERCADO:")
    print("   'LOJA DOS DESCONTOS' não está no dicionário")
    print()

    print("3. PREÇOS NO FORMATO INCOMUM:")
    print("   - Tem '%' no meio: '717,00%'")
    print("   - Preço final: '2,086' (com 3 decimais!)")
    print()

    print("=" * 70)
    print("💡 SOLUÇÕES:")
    print("=" * 70)
    print()

    print("Para fazer esta nota funcionar, precisamos:")
    print()
    print("1. Adicionar o supermercado:")
    print("   SUPERMERCADOS = {")
    print("       'LOJA DOS DESCONTOS': 'loja_descontos',")
    print("       ...")
    print("   }")
    print()

    print("2. Criar padrão MULTILINHAS:")
    print("   Este é um caso especial onde produto e preço")
    print("   estão em linhas diferentes!")
    print()
    print("   Vou criar uma função especial para este formato...")
    print()

    print("=" * 70)
    print("🔧 PRÓXIMO PASSO:")
    print("=" * 70)
    print()
    print("Vou ajustar o código para suportar este formato!")
    print()


if __name__ == "__main__":
    testar()
