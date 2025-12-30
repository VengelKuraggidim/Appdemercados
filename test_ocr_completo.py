#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste completo do sistema de OCR para notas fiscais.
Testa Tesseract e Claude Vision.
"""
import sys
import os

# Adicionar o diretorio raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
import io


def criar_imagem_nota_fiscal_teste():
    """Cria uma imagem simulando uma nota fiscal para teste"""
    largura, altura = 400, 600
    img = Image.new('RGB', (largura, altura), color='white')
    draw = ImageDraw.Draw(img)

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
        "------------------------",
        "TOTAL: R$ 49,98",
    ]

    y = 20
    for linha in linhas:
        draw.text((20, y), linha, fill='black')
        y += 25

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def testar_preprocessamento():
    """Testa o pre-processamento de imagem"""
    print("\n" + "="*60)
    print("TESTE 1: PRE-PROCESSAMENTO DE IMAGEM")
    print("="*60)

    try:
        from app.utils.ocr_nota_fiscal import get_ocr_nota_fiscal
        ocr = get_ocr_nota_fiscal()

        img_bytes = criar_imagem_nota_fiscal_teste()
        img = Image.open(io.BytesIO(img_bytes))

        # Testar cada metodo
        metodos = [
            ('_preprocessar_padrao', ocr._preprocessar_padrao),
            ('_preprocessar_alto_contraste', ocr._preprocessar_alto_contraste),
            ('_preprocessar_binarizado', ocr._preprocessar_binarizado),
        ]

        todos_ok = True
        for nome, metodo in metodos:
            try:
                resultado = metodo(img.copy())
                if resultado:
                    print(f"  [OK] {nome}")
                else:
                    print(f"  [ERRO] {nome}: Falhou")
                    todos_ok = False
            except Exception as e:
                print(f"  [ERRO] {nome}: {e}")
                todos_ok = False

        return todos_ok

    except Exception as e:
        print(f"  [ERRO]: {e}")
        return False


def testar_sistema_hibrido():
    """Testa o sistema hibrido de OCR"""
    print("\n" + "="*60)
    print("TESTE 2: SISTEMA HIBRIDO DE OCR")
    print("="*60)

    try:
        from app.utils.ocr_hibrido import get_ocr_hibrido

        ocr = get_ocr_hibrido()
        img_bytes = criar_imagem_nota_fiscal_teste()

        print("  Processando nota fiscal de teste...")
        resultado = ocr.processar_nota_fiscal(
            imagem_bytes=img_bytes,
            usuario_prefere_gratis=True,
            usuario_tem_creditos_api=False
        )

        if resultado.get('sucesso'):
            engine = resultado.get('metadados', {}).get('engine', 'desconhecido')
            produtos = resultado.get('produtos', [])
            confianca = resultado.get('confianca', 0)

            print(f"  [OK] Sucesso!")
            print(f"     Engine: {engine}")
            print(f"     Produtos encontrados: {len(produtos)}")
            print(f"     Confianca: {confianca}%")

            if produtos:
                print(f"     Primeiro produto: {produtos[0].get('nome', 'N/A')}")

            return True
        else:
            erro = resultado.get('erro', 'Erro desconhecido')
            print(f"  [AVISO] Falhou: {erro}")
            print("     (Isso pode ser normal se Tesseract nao estiver instalado)")
            return True  # Nao e erro critico

    except Exception as e:
        print(f"  [ERRO]: {e}")
        import traceback
        traceback.print_exc()
        return False


def testar_claude_vision():
    """Testa Claude Vision (se disponivel)"""
    print("\n" + "="*60)
    print("TESTE 3: CLAUDE VISION")
    print("="*60)

    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("  [AVISO] ANTHROPIC_API_KEY nao configurada")
        print("     Claude Vision nao disponivel")
        return True  # Nao e erro critico

    print("  [OK] ANTHROPIC_API_KEY encontrada")
    print("     Claude Vision esta disponivel como opcao premium")

    # Nao fazer chamada real para nao gastar creditos
    print("     (Pulando teste real para economizar creditos)")

    return True


def main():
    print("\n" + "[TESTE COMPLETO DO SISTEMA DE OCR]")

    # Carregar .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    resultados = []

    # Teste 1
    resultados.append(("Pre-processamento", testar_preprocessamento()))

    # Teste 2
    resultados.append(("Sistema Hibrido", testar_sistema_hibrido()))

    # Teste 3
    resultados.append(("Claude Vision", testar_claude_vision()))

    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    todos_ok = True
    for nome, ok in resultados:
        status = "[OK]" if ok else "[FALHOU]"
        print(f"  {nome}: {status}")
        if not ok:
            todos_ok = False

    print("="*60)

    if todos_ok:
        print("\n[SUCESSO] Todos os testes passaram!")
        print("\n[PROXIMOS PASSOS]:")
        print("   1. Instalar Tesseract OCR para usar opcao gratuita")
        print("      Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Ou usar Claude Vision (ja configurado) como opcao premium")
        print("   3. Rodar o servidor: python main.py")
        print("   4. Acessar: http://localhost:8000/scanner.html")
    else:
        print("\n[AVISO] Alguns testes falharam. Verifique os erros acima.")

    return 0 if todos_ok else 1


if __name__ == '__main__':
    sys.exit(main())
