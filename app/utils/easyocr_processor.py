"""
OCR usando EasyOCR - Gratuito e Offline
Alternativa open-source para Tesseract
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
import easyocr
from PIL import Image
import io
import numpy as np


class EasyOCRProcessor:
    """OCR usando EasyOCR para notas fiscais"""

    def __init__(self):
        """Inicializa EasyOCR com português"""
        # Inicializar reader (pode demorar na primeira vez)
        self.reader = easyocr.Reader(['pt'], gpu=False)  # gpu=False para CPU

        # Supermercados conhecidos
        self.supermercados = {
            'CARREFOUR': 'Carrefour',
            'PAO DE ACUCAR': 'Pão de Açúcar',
            'EXTRA': 'Extra',
            'WALMART': 'Walmart',
            'ASSAI': 'Assaí',
            'ATACADAO': 'Atacadão',
            'DIA': 'Dia',
            'BIG': 'Big',
            'CENTRO OESTE': 'Centro Oeste Comercial'
        }

    def extrair_produtos_nota_fiscal(
        self,
        imagem_bytes: bytes
    ) -> Dict:
        """
        Extrai produtos e informações de uma nota fiscal usando EasyOCR

        Args:
            imagem_bytes: Bytes da imagem da nota fiscal

        Returns:
            Dict com: sucesso, produtos[], total, supermercado, confianca
        """
        try:
            # Converter bytes para imagem
            imagem = Image.open(io.BytesIO(imagem_bytes))
            imagem_array = np.array(imagem)

            # Extrair texto com EasyOCR
            resultados = self.reader.readtext(imagem_array)

            # Extrair texto completo
            linhas = []
            confianca_media = 0

            for (bbox, texto, confianca) in resultados:
                linhas.append(texto)
                confianca_media += confianca

            if resultados:
                confianca_media = confianca_media / len(resultados)

            texto_completo = '\n'.join(linhas)

            # Identificar supermercado
            supermercado = self._identificar_supermercado(texto_completo)

            # Extrair produtos
            produtos = self._extrair_produtos(linhas)

            # Extrair total
            total = self._extrair_total(linhas)

            # Extrair data
            data_compra = self._extrair_data(texto_completo)

            return {
                'sucesso': True,
                'produtos': produtos,
                'total': total,
                'supermercado': supermercado,
                'data_compra': data_compra,
                'confianca': round(confianca_media * 100, 2),
                'linhas_extraidas': len(linhas),
                'metadados': {
                    'engine': 'EasyOCR',
                    'confianca_media': round(confianca_media * 100, 2),
                    'data_extracao': datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'produtos': [],
                'total': None,
                'supermercado': None,
                'confianca': 0,
                'metadados': {
                    'engine': 'EasyOCR',
                    'data_extracao': datetime.now().isoformat()
                }
            }

    def _identificar_supermercado(self, texto: str) -> Optional[str]:
        """Identifica o supermercado pelo texto"""
        texto_upper = texto.upper()

        for chave, nome in self.supermercados.items():
            if chave in texto_upper:
                return nome

        return 'Supermercado'

    def _extrair_produtos(self, linhas: List[str]) -> List[Dict]:
        """Extrai produtos das linhas de texto"""
        produtos = []

        # Padrão para linhas de produto: nome + preço
        # Exemplos: "ARROZ 5KG 19.99", "FEIJAO 1KG R$ 8.50"
        pattern_preco = r'(\d+[.,]\d{2})'

        palavras_ignorar = {
            'TOTAL', 'SUBTOTAL', 'DESCONTO', 'TROCO', 'DINHEIRO',
            'CARTAO', 'DEBITO', 'CREDITO', 'CUPOM', 'FISCAL',
            'CNPJ', 'CPF', 'DATA', 'HORA', 'OPERADOR'
        }

        for i, linha in enumerate(linhas):
            # Ignorar linhas muito curtas
            if len(linha.strip()) < 3:
                continue

            # Verificar se contém palavras a ignorar
            linha_upper = linha.upper()
            if any(palavra in linha_upper for palavra in palavras_ignorar):
                continue

            # Buscar preços na linha
            precos = re.findall(pattern_preco, linha)

            if precos:
                # Pegar o último preço (geralmente é o total)
                preco_str = precos[-1].replace(',', '.')

                try:
                    preco = float(preco_str)

                    # Ignorar preços muito baixos ou muito altos
                    if preco < 0.10 or preco > 10000:
                        continue

                    # Extrair nome do produto (remove o preço)
                    nome = re.sub(r'R?\$?\s*' + pattern_preco, '', linha)
                    nome = nome.strip()

                    # Limpar nome
                    nome = self._limpar_nome_produto(nome)

                    if len(nome) >= 3:  # Nome mínimo
                        produtos.append({
                            'nome': nome,
                            'preco': preco,
                            'linha': i + 1
                        })

                except ValueError:
                    continue

        return produtos

    def _limpar_nome_produto(self, nome: str) -> str:
        """Limpa e normaliza nome do produto"""
        # Remover códigos numéricos do início
        nome = re.sub(r'^\d{3,}\s+', '', nome)

        # Remover asteriscos e símbolos
        nome = re.sub(r'[*#@]', '', nome)

        # Remover espaços múltiplos
        nome = ' '.join(nome.split())

        # Capitalizar
        nome = nome.title()

        return nome.strip()

    def _extrair_total(self, linhas: List[str]) -> Optional[float]:
        """Extrai o valor total da nota fiscal"""
        pattern_total = r'TOTAL.*?(\d+[.,]\d{2})'

        # Buscar de trás para frente (total geralmente está no fim)
        for linha in reversed(linhas):
            if 'TOTAL' in linha.upper():
                match = re.search(pattern_total, linha.upper())
                if match:
                    try:
                        valor = float(match.group(1).replace(',', '.'))
                        return valor
                    except ValueError:
                        continue

        return None

    def _extrair_data(self, texto: str) -> Optional[str]:
        """Extrai data da compra"""
        # Padrões de data brasileira
        patterns = [
            r'(\d{2})[/-](\d{2})[/-](\d{4})',  # DD/MM/YYYY ou DD-MM-YYYY
            r'(\d{2})[/-](\d{2})[/-](\d{2})',  # DD/MM/YY
        ]

        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                dia, mes, ano = match.groups()

                # Corrigir ano de 2 dígitos
                if len(ano) == 2:
                    ano = '20' + ano

                try:
                    # Validar data
                    data = datetime(int(ano), int(mes), int(dia))
                    return data.strftime('%Y-%m-%d')
                except ValueError:
                    continue

        return None

    def calcular_confianca_produtos(self, produtos: List[Dict]) -> float:
        """
        Calcula confiança baseada na qualidade dos produtos extraídos

        Returns:
            Float de 0 a 100 representando a confiança
        """
        if not produtos:
            return 0.0

        pontos = 0
        max_pontos = 0

        # Critério 1: Quantidade de produtos (máx 30 pontos)
        if len(produtos) > 0:
            pontos += min(len(produtos) * 2, 30)
        max_pontos += 30

        # Critério 2: Produtos com nomes válidos (máx 40 pontos)
        nomes_validos = sum(1 for p in produtos if len(p['nome']) > 5)
        pontos += min(nomes_validos * 3, 40)
        max_pontos += 40

        # Critério 3: Preços em faixa razoável (máx 30 pontos)
        precos_validos = sum(
            1 for p in produtos
            if 0.50 <= p['preco'] <= 1000
        )
        pontos += min(precos_validos * 2, 30)
        max_pontos += 30

        return round((pontos / max_pontos) * 100, 2) if max_pontos > 0 else 0.0


def get_easyocr_processor() -> EasyOCRProcessor:
    """Factory function para criar instância do OCR"""
    return EasyOCRProcessor()
