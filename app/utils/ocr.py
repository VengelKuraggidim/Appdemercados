"""
OCR (Optical Character Recognition) para extrair preços de fotos
"""

from PIL import Image
import re
from typing import Dict, Optional, List
import io


class PrecoOCR:
    """Extrai informações de preço de imagens"""

    def __init__(self):
        self.use_easyocr = False
        self.reader = None

        # Try to use EasyOCR (better accuracy)
        try:
            import easyocr
            self.reader = easyocr.Reader(['pt', 'en'], gpu=False)
            self.use_easyocr = True
            print("✓ EasyOCR carregado com sucesso")
        except:
            # Fallback to Tesseract
            try:
                import pytesseract
                self.use_easyocr = False
                print("✓ Pytesseract carregado como fallback")
            except:
                print("⚠️  Nenhum OCR disponível. Instale: pip install easyocr ou pytesseract")

    def extrair_de_imagem(self, image_bytes: bytes) -> Dict:
        """
        Extrai informações de preço de uma imagem

        Returns:
            {
                'preco': float,
                'produto_nome': str,
                'marca': str,
                'texto_completo': str,
                'confianca': float
            }
        """
        try:
            # Carregar imagem
            image = Image.open(io.BytesIO(image_bytes))

            # Extrair texto da imagem
            if self.use_easyocr and self.reader:
                texto = self._extrair_com_easyocr(image)
            else:
                texto = self._extrair_com_tesseract(image)

            if not texto:
                return {
                    'erro': 'Não foi possível extrair texto da imagem',
                    'texto_completo': ''
                }

            # Processar texto extraído
            resultado = self._processar_texto(texto)
            resultado['texto_completo'] = texto

            return resultado

        except Exception as e:
            return {
                'erro': f'Erro ao processar imagem: {str(e)}',
                'texto_completo': ''
            }

    def _extrair_com_easyocr(self, image: Image) -> str:
        """Extrai texto usando EasyOCR"""
        try:
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # EasyOCR
            import numpy as np
            img_array = np.array(image)
            results = self.reader.readtext(img_array)

            # Juntar todo o texto
            texto = ' '.join([result[1] for result in results])
            return texto
        except Exception as e:
            print(f"Erro no EasyOCR: {e}")
            return ""

    def _extrair_com_tesseract(self, image: Image) -> str:
        """Extrai texto usando Tesseract OCR"""
        try:
            import pytesseract

            # Converter para modo adequado
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Configuração para português
            config = '--psm 6 -l por'
            texto = pytesseract.image_to_string(image, config=config)

            return texto
        except Exception as e:
            print(f"Erro no Tesseract: {e}")
            return ""

    def _processar_texto(self, texto: str) -> Dict:
        """
        Processa o texto extraído para identificar preço, produto e marca
        """
        resultado = {
            'preco': None,
            'produto_nome': None,
            'marca': None,
            'precos_encontrados': [],
            'confianca': 0.0
        }

        # Extrair preços (R$, reais, vírgula/ponto)
        precos = self._extrair_precos(texto)
        resultado['precos_encontrados'] = precos

        if precos:
            # Pegar o maior preço (geralmente é o preço principal)
            resultado['preco'] = max(precos)
            resultado['confianca'] = 0.8

        # Tentar identificar produto
        produto_info = self._identificar_produto(texto)
        if produto_info:
            resultado['produto_nome'] = produto_info.get('nome')
            resultado['marca'] = produto_info.get('marca')
            resultado['confianca'] = min(resultado['confianca'] + 0.2, 1.0)

        return resultado

    def _extrair_precos(self, texto: str) -> List[float]:
        """Extrai todos os preços do texto"""
        precos = []

        # Padrões comuns de preço
        patterns = [
            r'R\$?\s*(\d+)[,.](\d{2})',  # R$ 12,90 ou R$ 12.90
            r'(\d+)[,.](\d{2})\s*reais?',  # 12,90 reais
            r'por\s+R?\$?\s*(\d+)[,.](\d{2})',  # por R$ 12,90
            r'(\d+)[,.](\d{2})',  # 12,90 (genérico)
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, texto, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 2:
                        reais = match.group(1)
                        centavos = match.group(2)
                        preco = float(f"{reais}.{centavos}")

                        # Filtrar preços absurdos
                        if 0.01 <= preco <= 10000:
                            precos.append(preco)
                except:
                    continue

        return sorted(set(precos), reverse=True)

    def _identificar_produto(self, texto: str) -> Optional[Dict]:
        """
        Tenta identificar o produto e marca do texto
        """
        texto_lower = texto.lower()

        # Lista de produtos comuns
        produtos_conhecidos = {
            'arroz': ['arroz', 'rice'],
            'feijão': ['feijao', 'feijão', 'beans'],
            'café': ['cafe', 'café', 'coffee'],
            'açúcar': ['acucar', 'açúcar', 'açucar', 'sugar'],
            'óleo': ['oleo', 'óleo', 'oil'],
            'leite': ['leite', 'milk'],
            'macarrão': ['macarrao', 'macarrão', 'pasta'],
            'sal': ['sal', 'salt'],
            'farinha': ['farinha', 'flour'],
        }

        # Marcas comuns
        marcas_conhecidas = [
            'tio joão', 'tio joao', 'camil', 'pilão', 'pilao',
            'união', 'uniao', 'liza', 'soya', 'italac', 'nestle',
            'barilla', 'renata', 'type', 'urbano', 'abc', 'quero',
            'kitano', 'maggi', 'vigor', 'parmalat', 'castelo'
        ]

        # Identificar produto
        produto_encontrado = None
        for produto, keywords in produtos_conhecidos.items():
            for keyword in keywords:
                if keyword in texto_lower:
                    produto_encontrado = produto
                    break
            if produto_encontrado:
                break

        # Identificar marca
        marca_encontrada = None
        for marca in marcas_conhecidas:
            if marca in texto_lower:
                marca_encontrada = marca.title()
                break

        if produto_encontrado or marca_encontrada:
            return {
                'nome': produto_encontrado,
                'marca': marca_encontrada
            }

        return None


# Singleton instance
_ocr_instance = None

def get_ocr_instance():
    """Get or create OCR instance"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PrecoOCR()
    return _ocr_instance
