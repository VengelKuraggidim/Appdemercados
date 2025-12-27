#!/usr/bin/env python3
"""
Script para testar o OCR com texto de exemplo
Simula uma nota fiscal típica
"""

from app.utils.ocr_nota_fiscal import NotaFiscalOCR

# Texto de exemplo de uma nota fiscal típica
texto_nota_exemplo = """
CARREFOUR COMERCIO E INDUSTRIA LTDA
RUA EXEMPLO 123 - SAO PAULO - SP
CNPJ: 12.345.678/0001-90
CUPOM FISCAL

DATA: 03/10/2025  HORA: 14:30:25

CODIGO  DESCRICAO           QTD  UN  PRECO
-----------------------------------------------
001     ARROZ TIPO 1        1    KG  15,90
002     FEIJAO PRETO        1    KG  8,50
003     OLEO DE SOJA 900ML  1    UN  7,90
004     CAFE PILAO 500G     1    UN  12,50
005     ACUCAR REFINADO     1    KG  4,20
006     SAL REFINADO        1    UN  2,50
007     MACARRAO ESPAGUETE  2    PC  3,80
008     MOLHO DE TOMATE     1    UN  2,90
009     LEITE INTEGRAL 1L   2    UN  4,50
010     OVOS BRANCOS 12UN   1    CX  11,90

SUBTOTAL:                         82,10
DESCONTO:                          2,10
-----------------------------------------------
TOTAL:                      R$    80,00

FORMA DE PAGAMENTO: CARTAO DEBITO

OBRIGADO PELA PREFERENCIA!
VOLTE SEMPRE!
"""

def testar_ocr():
    print("=" * 60)
    print("🔬 TESTE DE OCR - Nota Fiscal de Exemplo")
    print("=" * 60)
    print()

    ocr = NotaFiscalOCR()

    # Testar identificação de supermercado
    print("1️⃣ TESTANDO IDENTIFICAÇÃO DE SUPERMERCADO:")
    supermercado = ocr.identificar_supermercado(texto_nota_exemplo)
    print(f"   Resultado: {supermercado or '❌ Não identificado'}")
    print()

    # Testar extração de data
    print("2️⃣ TESTANDO EXTRAÇÃO DE DATA:")
    data = ocr.extrair_data(texto_nota_exemplo)
    print(f"   Resultado: {data.strftime('%d/%m/%Y') if data else '❌ Não encontrada'}")
    print()

    # Testar extração de produtos
    print("3️⃣ TESTANDO EXTRAÇÃO DE PRODUTOS:")
    produtos = ocr.extrair_produtos(texto_nota_exemplo)
    print(f"   Total encontrado: {len(produtos)} produtos")
    print()

    if produtos:
        print("   Produtos extraídos:")
        for i, prod in enumerate(produtos, 1):
            print(f"   {i}. {prod['nome']:30} R$ {prod['preco']:6.2f} ({prod['quantidade']}x)")
    else:
        print("   ❌ Nenhum produto encontrado")
    print()

    # Testar extração de total
    print("4️⃣ TESTANDO EXTRAÇÃO DE TOTAL:")
    total = ocr.extrair_total(texto_nota_exemplo)
    print(f"   Resultado: R$ {total:.2f}" if total else "   ❌ Não encontrado")
    print()

    # Resumo
    print("=" * 60)
    print("📊 RESUMO DO TESTE:")
    print("=" * 60)

    soma_produtos = sum(p['preco'] * p['quantidade'] for p in produtos) if produtos else 0

    print(f"✓ Supermercado: {supermercado or 'Não identificado'}")
    print(f"✓ Data: {data.strftime('%d/%m/%Y') if data else 'Não encontrada'}")
    print(f"✓ Produtos: {len(produtos)}/10 (esperado)")
    print(f"✓ Soma produtos: R$ {soma_produtos:.2f}")
    print(f"✓ Total nota: R$ {total:.2f}" if total else "✓ Total: Não encontrado")

    if total and produtos:
        diferenca = abs(total - soma_produtos)
        percentual = (diferenca / total * 100) if total > 0 else 0
        print(f"✓ Diferença: R$ {diferenca:.2f} ({percentual:.1f}%)")

        if percentual < 5:
            print("\n✅ VALIDAÇÃO: Total bate com soma dos produtos!")
        else:
            print(f"\n⚠️  VALIDAÇÃO: Diferença de {percentual:.1f}% (pode ter desconto/taxas)")

    print()
    print("=" * 60)
    print("💡 DICAS:")
    print("=" * 60)
    print()

    if not supermercado:
        print("🔸 Supermercado não identificado:")
        print("   - Verifique se o nome está no dicionário SUPERMERCADOS")
        print("   - Adicione variações do nome se necessário")
        print()

    if not data:
        print("🔸 Data não encontrada:")
        print("   - Verifique o formato da data no texto")
        print("   - Adicione o padrão específico em extrair_data()")
        print()

    if len(produtos) < 10:
        print("🔸 Poucos produtos encontrados:")
        print("   - Verifique o formato das linhas no texto")
        print("   - Pode precisar ajustar os padrões regex")
        print("   - Use o Debug OCR no app para ver o texto real")
        print()

    print("📝 Para testar com SUA nota fiscal:")
    print("   1. Use o Debug OCR no app: http://localhost:8000/scanner.html")
    print("   2. Copie o texto extraído")
    print("   3. Cole neste script substituindo 'texto_nota_exemplo'")
    print("   4. Execute: python3 testar_ocr_exemplo.py")
    print()


if __name__ == "__main__":
    testar_ocr()
