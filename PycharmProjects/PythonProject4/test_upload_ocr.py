#!/usr/bin/env python3
"""
Script de teste para verificar se o OCR está funcionando
"""
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Criar uma imagem de teste simples com texto
def criar_nota_fiscal_teste():
    """Cria uma imagem de nota fiscal fictícia"""
    img = Image.new('RGB', (600, 800), color='white')
    draw = ImageDraw.Draw(img)

    # Texto da nota fiscal
    texto = """
    CARREFOUR SUPERMERCADOS

    CUPOM FISCAL

    Data: 05/10/2024

    001 ARROZ TIPO 1 5KG
    1UN 25,90  25,90

    002 FEIJAO PRETO 1KG
    2UN 8,50  17,00

    003 OLEO DE SOJA 900ML
    1UN 6,99  6,99

    TOTAL: R$ 49,89
    """

    y = 50
    for linha in texto.strip().split('\n'):
        draw.text((50, y), linha.strip(), fill='black')
        y += 25

    # Salvar em BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer

# Testar endpoint
def testar_ocr():
    url = "http://localhost:8000/api/debug-ocr"

    # Criar imagem de teste
    imagem = criar_nota_fiscal_teste()

    files = {
        'file': ('nota_fiscal.png', imagem, 'image/png')
    }

    print("Enviando requisição para:", url)

    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"\nStatus: {response.status_code}")
        print(f"\nResposta:")
        print(response.json() if response.headers.get('content-type') == 'application/json' else response.text)
    except Exception as e:
        print(f"\nErro: {e}")

if __name__ == "__main__":
    testar_ocr()
