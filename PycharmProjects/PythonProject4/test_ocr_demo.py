#!/usr/bin/env python3
"""
Demo do OCR sem precisar de imagem real
Mostra como o sistema funciona
"""

from app.utils.ocr import PrecoOCR

# Simular texto extraído de uma foto
textos_exemplo = [
    """
    ARROZ TIO JOÃO
    TIPO 1 - 5KG
    R$ 23,90
    PROMOÇÃO
    """,

    """
    Feijão Carioca
    Marca: CAMIL
    1kg
    Por R$ 7,50
    """,

    """
    CAFÉ PILÃO
    Torrado e Moído
    500g
    R$ 14.90
    """,

    """
    AÇÚCAR UNIÃO
    Cristal 1kg
    Preço: 4,20 reais
    """,
]

print("="*60)
print("🧪 TESTE DO SISTEMA OCR - SIMULAÇÃO")
print("="*60)
print()
print("Simulando extração de texto de fotos...\n")

ocr = PrecoOCR()

for i, texto in enumerate(textos_exemplo, 1):
    print(f"\n{'─'*60}")
    print(f"📸 FOTO {i}:")
    print(f"{'─'*60}")
    print(f"Texto simulado:")
    print(texto.strip())
    print()

    # Processar texto
    resultado = ocr._processar_texto(texto)

    print("✨ Dados Extraídos:")
    print(f"   💰 Preço: R$ {resultado['preco']:.2f}" if resultado['preco'] else "   ❌ Preço não encontrado")

    if resultado['produto_nome']:
        print(f"   📦 Produto: {resultado['produto_nome']}")

    if resultado['marca']:
        print(f"   🏷️  Marca: {resultado['marca']}")

    print(f"   📊 Confiança: {resultado['confianca']*100:.0f}%")

    if resultado['precos_encontrados']:
        print(f"   📋 Todos os preços encontrados: {resultado['precos_encontrados']}")

print()
print("="*60)
print("✅ DEMO CONCLUÍDA!")
print("="*60)
print()
print("💡 Para usar com fotos reais:")
print("   1. Instale EasyOCR: pip install easyocr")
print("   2. Ou Tesseract: apt-get install tesseract-ocr")
print("   3. Acesse: http://localhost:3000/foto.html")
print()
print("🌐 O sistema funciona melhor com:")
print("   • Fotos nítidas e bem iluminadas")
print("   • Foco no preço e nome do produto")
print("   • Etiquetas de preço padrão de supermercado")
