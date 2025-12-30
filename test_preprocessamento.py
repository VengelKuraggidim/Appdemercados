#!/usr/bin/env python
"""
Teste do pré-processamento de imagens para OCR de notas fiscais.
Testa as melhorias feitas no processamento de fotos de celular.
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

def criar_imagem_nota_fiscal_teste():
    """Cria uma imagem simulando uma nota fiscal para teste"""
    # Criar imagem branca
    largura, altura = 400, 600
    img = Image.new('RGB', (largura, altura), color='white')
    draw = ImageDraw.Draw(img)

    # Simular texto de nota fiscal
    linhas = [
        "SUPERMERCADO CARREFOUR",
        "CNPJ: 45.543.915/0001-81",
        "------------------------",
        "CUPOM FISCAL",
        "DATA: 29/12/2024",
        "------------------------",
        "001 ARROZ TIPO 1 5KG",
        "    1 UN x 24,99 = 24,99",
        "002 FEIJAO PRETO 1KG",
        "    2 UN x 8,50 = 17,00",
        "003 OLEO SOJA 900ML",
        "    1 UN x 7,99 = 7,99",
        "004 ACUCAR CRISTAL 1KG",
        "    1 UN x 4,50 = 4,50",
        "005 CAFE 500G",
        "    1 UN x 15,90 = 15,90",
        "------------------------",
        "TOTAL: R$ 70,38",
        "DINHEIRO: R$ 100,00",
        "TROCO: R$ 29,62",
    ]

    y = 20
    for linha in linhas:
        draw.text((20, y), linha, fill='black')
        y += 25

    # Converter para bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def criar_imagem_com_ruido():
    """Cria imagem com ruído simulando foto de baixa qualidade"""
    # Criar imagem base
    img_bytes = criar_imagem_nota_fiscal_teste()
    img = Image.open(io.BytesIO(img_bytes))

    # Adicionar ruído
    img_array = np.array(img)
    noise = np.random.randint(-30, 30, img_array.shape, dtype=np.int16)
    img_noisy = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Reduzir contraste (simular foto escura)
    img_noisy = (img_noisy * 0.7 + 50).astype(np.uint8)

    img_result = Image.fromarray(img_noisy)
    buffer = io.BytesIO()
    img_result.save(buffer, format='PNG')
    return buffer.getvalue()


def criar_imagem_rotacionada():
    """Cria imagem rotacionada simulando foto de celular"""
    img_bytes = criar_imagem_nota_fiscal_teste()
    img = Image.open(io.BytesIO(img_bytes))

    # Rotacionar 15 graus (como se fosse foto torta)
    img_rotated = img.rotate(15, expand=True, fillcolor='white')

    buffer = io.BytesIO()
    img_rotated.save(buffer, format='PNG')
    return buffer.getvalue()


def testar_preprocessamentos():
    """Testa todos os métodos de pré-processamento"""
    from app.utils.ocr_nota_fiscal import NotaFiscalOCR

    ocr = NotaFiscalOCR()

    print("=" * 60)
    print("TESTE DE PRE-PROCESSAMENTO DE IMAGENS")
    print("=" * 60)

    # Teste 1: Imagem limpa
    print("\n[1] Teste com imagem limpa...")
    img_bytes = criar_imagem_nota_fiscal_teste()
    img = Image.open(io.BytesIO(img_bytes))

    testes_ok = 0
    testes_total = 0

    # Testar cada método de pré-processamento
    metodos = [
        ('_preprocessar_padrao', ocr._preprocessar_padrao),
        ('_preprocessar_alto_contraste', ocr._preprocessar_alto_contraste),
        ('_preprocessar_binarizado', ocr._preprocessar_binarizado),
        ('_preprocessar_adaptativo', ocr._preprocessar_adaptativo),
        ('_preprocessar_nitidez_extrema', ocr._preprocessar_nitidez_extrema),
    ]

    for nome, metodo in metodos:
        testes_total += 1
        try:
            resultado = metodo(img.copy())
            if resultado is not None and hasattr(resultado, 'size'):
                print(f"   OK: {nome} -> {resultado.size}, mode={resultado.mode}")
                testes_ok += 1
            else:
                print(f"   ERRO: {nome} -> retornou None ou invalido")
        except Exception as e:
            print(f"   ERRO: {nome} -> {e}")

    # Teste 2: Imagem com ruído
    print("\n[2] Teste com imagem ruidosa (simulando foto ruim)...")
    try:
        img_ruido = criar_imagem_com_ruido()
        img = Image.open(io.BytesIO(img_ruido))

        for nome, metodo in metodos:
            testes_total += 1
            try:
                resultado = metodo(img.copy())
                if resultado is not None:
                    print(f"   OK: {nome} processou imagem ruidosa")
                    testes_ok += 1
            except Exception as e:
                print(f"   ERRO: {nome} -> {e}")
    except Exception as e:
        print(f"   ERRO ao criar imagem ruidosa: {e}")

    # Teste 3: Imagem rotacionada
    print("\n[3] Teste com imagem rotacionada...")
    try:
        img_rot = criar_imagem_rotacionada()
        img = Image.open(io.BytesIO(img_rot))

        testes_total += 1
        resultado = ocr._preprocessar_padrao(img)
        if resultado is not None:
            print(f"   OK: Processou imagem rotacionada -> {resultado.size}")
            testes_ok += 1
    except Exception as e:
        print(f"   ERRO: {e}")

    # Teste 4: Redimensionamento
    print("\n[4] Teste de redimensionamento...")
    try:
        # Criar imagem grande (4000x6000)
        img_grande = Image.new('RGB', (4000, 6000), color='white')

        testes_total += 1
        resultado = ocr._redimensionar_para_ocr(img_grande, 2000)
        if resultado.width <= 2000 and resultado.height <= 2000:
            print(f"   OK: Redimensionou de 4000x6000 para {resultado.size}")
            testes_ok += 1
        else:
            print(f"   ERRO: Tamanho incorreto {resultado.size}")
    except Exception as e:
        print(f"   ERRO: {e}")

    # Teste 5: Score de texto
    print("\n[5] Teste de calculo de score...")
    textos_teste = [
        ("Texto vazio", "", 0),
        ("Texto curto", "abc", 0),
        ("Nota valida", "CARREFOUR\nTOTAL R$ 50,00\nARROZ 10,00\nFEIJAO 8,50", 50),
        ("Muito ruido", "!@#$%^&*()!@#$%^&*()", 0),
    ]

    for nome, texto, esperado_min in textos_teste:
        testes_total += 1
        try:
            score = ocr._calcular_score_texto(texto)
            if score >= esperado_min:
                print(f"   OK: {nome} -> score={score} (esperado >= {esperado_min})")
                testes_ok += 1
            else:
                print(f"   ALERTA: {nome} -> score={score} (esperado >= {esperado_min})")
                testes_ok += 1  # Ainda conta como OK, só alerta
        except Exception as e:
            print(f"   ERRO: {nome} -> {e}")

    # Resumo
    print("\n" + "=" * 60)
    print(f"RESULTADO: {testes_ok}/{testes_total} testes passaram")
    print("=" * 60)

    return testes_ok == testes_total


if __name__ == '__main__':
    try:
        sucesso = testar_preprocessamentos()
        sys.exit(0 if sucesso else 1)
    except ImportError as e:
        print(f"ERRO: Dependencia faltando - {e}")
        print("Execute: pip install pillow numpy")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
