"""
OCR para Notas Fiscais de Supermercado
Reconhece e extrai produtos e preços de cupons fiscais
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
import pytesseract
from PIL import Image
import io


class NotaFiscalOCR:
    """OCR especializado em notas fiscais de supermercado"""

    # Padrões de supermercados conhecidos
    SUPERMERCADOS = {
        'CARREFOUR': 'carrefour',
        'PAO DE ACUCAR': 'pao_acucar',
        'PÃO DE AÇUCAR': 'pao_acucar',
        'EXTRA': 'extra',
        'ATACADAO': 'atacadao',
        'ATACADÃO': 'atacadao',
        'DIA': 'dia',
        'ASSAI': 'assai',
        'WALMART': 'walmart',
        'BIG': 'big',
        'MAMBO': 'mambo',
        'LOJA DOS DESCONTOS': 'loja_descontos',
        'DESCONTOS': 'loja_descontos'
    }

    def __init__(self):
        # Configurar Tesseract para português
        self.tesseract_config = '--oem 3 --psm 6 -l por'

        # Palavras-chave e códigos que NÃO são produtos
        self.palavras_ignorar = [
            'TOTAL', 'SUBTOTAL', 'DESCONTO', 'TROCO', 'DINHEIRO', 'CARTAO', 'CARTÃO',
            'DEBITO', 'DÉBITO', 'CREDITO', 'CRÉDITO', 'CUPOM', 'FISCAL', 'DATA', 'HORA',
            'CNPJ', 'CPF', 'ENDERECO', 'ENDEREÇO', 'TELEFONE', 'OBRIGADO', 'VOLTE',
            'IMPOSTOS', 'VERSAO', 'VERSÃO', 'ECF', 'FAB', 'CCF', 'COO',
            'ACRESCIMO', 'ACRÉSCIMO', 'CASHBACK', 'ECONOMIA', 'OPERADOR',
            'LOJA', 'FILIAL', 'CAIXA', 'PDV', 'TERMINAL', 'SERIE', 'SÉRIE',
            'ITEN', 'QTD', 'VLR', 'UN', 'CÓD', 'COD', 'PRODUTO',
            # Códigos numéricos comuns (EAN, NCM, etc)
            'EAN', 'NCM', 'GTIN', 'CST', 'CFOP', 'ICMS', 'PIS', 'COFINS'
        ]

        # Padrões de códigos para remover (geralmente são EAN/SKU no início)
        self.padroes_codigo_remover = [
            r'^\d{7,13}\s*',  # EAN/SKU (7-13 dígitos)
            r'^\d{2,5}\s+\d{6,13}\s*',  # Código + EAN
            r'^[A-Z]{2,4}\d+\s*',  # Código alfanumérico
        ]

    def extrair_texto(self, imagem_bytes: bytes) -> str:
        """Extrai texto da imagem da nota fiscal"""
        try:
            imagem = Image.open(io.BytesIO(imagem_bytes))

            # Melhorar qualidade da imagem
            from PIL import ImageEnhance

            # Converter para RGB primeiro se necessário
            if imagem.mode not in ('L', 'RGB'):
                imagem = imagem.convert('RGB')

            # Aumentar contraste
            enhancer = ImageEnhance.Contrast(imagem)
            imagem = enhancer.enhance(2.0)

            # Converter para escala de cinza
            imagem = imagem.convert('L')

            # Aumentar nitidez
            enhancer = ImageEnhance.Sharpness(imagem)
            imagem = enhancer.enhance(2.0)

            # Extrair texto com configuração otimizada
            # PSM 6 = assume um bloco uniforme de texto
            custom_config = r'--oem 3 --psm 6 -l por'
            texto = pytesseract.image_to_string(imagem, config=custom_config)

            return texto

        except Exception as e:
            raise Exception(f"Erro ao processar imagem: {str(e)}")

    def identificar_supermercado(self, texto: str) -> Optional[str]:
        """Identifica o supermercado pela nota fiscal"""
        texto_upper = texto.upper()

        for nome, slug in self.SUPERMERCADOS.items():
            if nome in texto_upper:
                return slug

        return None

    def extrair_data(self, texto: str) -> Optional[datetime]:
        """Extrai a data da compra"""
        # Padrões de data comuns em notas fiscais
        padroes = [
            # DD/MM/YYYY com separadores
            r'(?:DATA|EMISSAO|EMISSÃO|CUPOM).*?(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})',
            r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})',
            # DD/MM/YY
            r'(?:DATA|EMISSAO|EMISSÃO|CUPOM).*?(\d{2})[/\-\.](\d{2})[/\-\.](\d{2})',
            r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{2})',
            # Formatos sem separador
            r'(\d{2})(\d{2})(\d{4})',
        ]

        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                try:
                    grupos = match.groups()
                    dia = int(grupos[-3])
                    mes = int(grupos[-2])
                    ano = grupos[-1]

                    if len(ano) == 2:
                        ano = '20' + ano

                    ano = int(ano)

                    # Validar data
                    if 1 <= dia <= 31 and 1 <= mes <= 12 and 2000 <= ano <= 2030:
                        return datetime(ano, mes, dia)
                except:
                    continue

        return None

    def extrair_produtos(self, texto: str) -> List[Dict]:
        """
        Extrai produtos e preços do texto da nota fiscal
        Foca apenas em: nome do produto, unidade/quantidade e preço
        Ignora códigos EAN, SKU e outras informações desnecessárias

        Formato comum de linhas de produto:
        - PRODUTO NOME          QTD  PRECO
        - 001 ARROZ TIPO 1      1KG  R$ 15,90
        - FEIJAO PRETO          1    8.50
        """
        produtos = []
        linhas = texto.split('\n')

        # Primeiro tentar formato de 2 linhas (produto + preço separados)
        produtos_multilinhas = self._extrair_produtos_multilinhas(linhas, self.palavras_ignorar)
        if produtos_multilinhas:
            return produtos_multilinhas

        # Se não encontrou, tentar padrão normal (1 linha)
        # Padrões melhorados para capturar produtos
        padroes = [
            # Padrão 1: Código + Nome + Quantidade + Unidade + Preço
            r'^(\d+)\s+(.+?)\s+(\d+[.,]?\d*)\s*(UN|KG|LT|L|PC|CX|PCT)?\s+(?:R\$|RS)?\s*(\d+[.,]\d{2})',

            # Padrão 2: Nome + Quantidade + Preço
            r'^(.+?)\s+(\d+[.,]?\d*)\s*(?:UN|KG|LT|L|PC|CX|PCT)?\s+(?:R\$|RS)?\s*(\d+[.,]\d{2})',

            # Padrão 3: Nome + Preço (sem quantidade explícita)
            r'^(.+?)\s+(?:R\$|RS)?\s*(\d+[.,]\d{2})\s*$',

            # Padrão 4: Código + Nome + Preço
            r'^(\d+)\s+(.+?)\s+(?:R\$|RS)?\s*(\d+[.,]\d{2})',
        ]

        for linha in linhas:
            linha_original = linha.strip()

            # Pular linhas vazias ou muito curtas
            if not linha_original or len(linha_original) < 5:
                continue

            # Pular linhas com palavras-chave (usando lista do __init__)
            if any(palavra in linha_original.upper() for palavra in self.palavras_ignorar):
                continue

            # Pular linhas que são apenas códigos (EAN, SKU, etc)
            # Exemplos: "7896015289324", "002 57192502", "EAN 789601528"
            if re.match(r'^(?:EAN|SKU|COD|CODIGO)?\s*\d{7,13}\s*$', linha_original, re.IGNORECASE):
                continue

            # Pular linhas que contêm apenas códigos técnicos (NCM, CST, CFOP, etc)
            if re.match(r'^(?:NCM|CST|CFOP|ICMS|PIS|COFINS).*', linha_original, re.IGNORECASE):
                continue

            produto_encontrado = False

            for i, padrao in enumerate(padroes):
                match = re.search(padrao, linha_original, re.IGNORECASE)

                if match:
                    grupos = match.groups()

                    try:
                        if i == 0:  # Padrão com código
                            codigo = grupos[0]
                            nome_produto = grupos[1].strip()
                            quantidade = grupos[2].replace(',', '.') if grupos[2] else '1'
                            preco_str = grupos[4].replace(',', '.')
                        elif i == 1:  # Nome + Qtd + Preço
                            nome_produto = grupos[0].strip()
                            quantidade = grupos[1].replace(',', '.') if grupos[1] else '1'
                            preco_str = grupos[2].replace(',', '.')
                        elif i == 2:  # Nome + Preço
                            nome_produto = grupos[0].strip()
                            quantidade = '1'
                            preco_str = grupos[1].replace(',', '.')
                        else:  # Código + Nome + Preço
                            nome_produto = grupos[1].strip()
                            quantidade = '1'
                            preco_str = grupos[2].replace(',', '.')

                        # Limpar códigos do início do nome do produto
                        # Remove EAN, SKU e códigos numéricos longos
                        for padrao_codigo in self.padroes_codigo_remover:
                            nome_produto = re.sub(padrao_codigo, '', nome_produto)

                        # Limpar código inicial se tiver (números no início)
                        nome_produto = re.sub(r'^\d+\s+', '', nome_produto)

                        # Limpar caracteres especiais desnecessários
                        nome_produto = re.sub(r'^["\'\—\-\s]+', '', nome_produto)
                        nome_produto = nome_produto.strip()

                        # Validações
                        # Nome deve ter pelo menos 3 caracteres e não pode ser só números
                        if len(nome_produto) >= 3 and not nome_produto.isdigit():
                            preco = float(preco_str)
                            qtd = float(quantidade)

                            # Filtrar preços muito altos ou baixos
                            if 0.10 < preco < 1000 and 0 < qtd <= 100:
                                produtos.append({
                                    'nome': nome_produto.title(),  # Capitalize primeira letra
                                    'preco': preco,
                                    'quantidade': qtd
                                })
                                produto_encontrado = True
                                break

                    except (ValueError, IndexError):
                        continue

        return produtos

    def _extrair_produtos_multilinhas(self, linhas: List[str], palavras_ignorar: List[str]) -> List[Dict]:
        """
        Extrai produtos de notas onde produto e preço estão em linhas separadas

        Formato moderno (Brasil 2025):
        Linha 1: 001 2667 FILE PEITO SUPER FRANGO Kg RESF
        Linha 2: 1,855KG 19,98  37,06
                 ↑quantidade ↑preço/kg ↑total (ignoramos o total, usamos preço/kg)
        """
        produtos = []
        i = 0

        while i < len(linhas) - 1:
            linha_atual = linhas[i].strip()
            linha_seguinte = linhas[i + 1].strip()

            # Pular linhas vazias
            if not linha_atual or not linha_seguinte:
                i += 1
                continue

            # Pular se tem palavras-chave
            if any(palavra in linha_atual.upper() for palavra in palavras_ignorar):
                i += 1
                continue

            # Padrão: Linha 1 = Código do item + Código do produto + Nome do produto
            # Exemplo: 001 2667 FILE PEITO SUPER FRANGO Kg RESF
            # ou: 002 1234 ARROZ TIPO 1 5KG
            padroes_produto = [
                r'^(\d{3})\s+(\d+)\s+(.+)$',  # Formato: 001 2667 NOME DO PRODUTO
            ]

            match_produto = None
            for padrao in padroes_produto:
                match_produto = re.search(padrao, linha_atual)
                if match_produto:
                    break

            if match_produto:
                # Pegar apenas o nome do produto (grupo 3)
                nome_produto = match_produto.group(3).strip()

                # Limpar sufixos comuns (Kg, UN, RESF, etc)
                nome_produto = re.sub(r'\s+(KG|UN|LT|L|PC|RESF|CONG|PCT|CX)\s*$', '', nome_produto, flags=re.IGNORECASE)
                nome_produto = nome_produto.strip()

                # Linha 2 = Quantidade + Unidade + Preço Unitário + Total
                # Exemplos:
                # 1,855KG 19,98  37,06
                # 2UN 5,50  11,00
                # 0,500KG 12,90  6,45
                padroes_preco = [
                    # Padrão: quantidade+unidade preço_unitario total
                    r'^(\d+[.,]?\d*)\s*(KG|UN|LT|L|PC|PCT|CX)?\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})',
                ]

                for padrao_preco in padroes_preco:
                    match_preco = re.search(padrao_preco, linha_seguinte, re.IGNORECASE)

                    if match_preco:
                        try:
                            quantidade_str = match_preco.group(1).replace(',', '.')
                            unidade = match_preco.group(2) or 'UN'
                            preco_unitario_str = match_preco.group(3).replace(',', '.')
                            # total_str = match_preco.group(4)  # Não precisamos do total

                            quantidade = float(quantidade_str)
                            preco_unitario = float(preco_unitario_str)

                            # Validar
                            if len(nome_produto) >= 3 and 0.10 < preco_unitario < 1000 and 0 < quantidade <= 100:
                                produtos.append({
                                    'nome': nome_produto.title(),
                                    'preco': preco_unitario,  # preço unitário (por kg, por unidade, etc)
                                    'quantidade': quantidade
                                })

                                i += 2  # Pula as duas linhas
                                break  # Sai do loop de padrões

                        except (ValueError, IndexError):
                            continue

            i += 1

        return produtos

    def extrair_total(self, texto: str) -> Optional[float]:
        """Extrai o valor total da compra"""
        # Padrões para total (em ordem de prioridade)
        padroes_total = [
            # TOTAL: R$ 80,00
            r'TOTAL[:\s]+(?:R\$|RS)?\s*(\d+[.,]\d{2})',
            # TOTAL         80,00
            r'TOTAL\s+(\d+[.,]\d{2})',
            # VALOR TOTAL: 80,00
            r'VALOR\s+TOTAL[:\s]+(?:R\$|RS)?\s*(\d+[.,]\d{2})',
            # TOTAL GERAL: 80,00
            r'TOTAL\s+GERAL[:\s]+(?:R\$|RS)?\s*(\d+[.,]\d{2})',
            # VLR TOTAL: 80,00
            r'VLR\s+TOTAL[:\s]+(?:R\$|RS)?\s*(\d+[.,]\d{2})',
        ]

        texto_upper = texto.upper()

        for padrao in padroes_total:
            match = re.search(padrao, texto_upper)
            if match:
                try:
                    total_str = match.group(1).replace(',', '.')
                    total = float(total_str)
                    # Validar se é um valor razoável (entre 1 e 10000)
                    if 1.0 < total < 10000:
                        return total
                except:
                    continue

        return None

    def processar_nota_fiscal(self, imagem_bytes: bytes) -> Dict:
        """
        Processa uma nota fiscal completa e extrai todas as informações
        """
        try:
            # Extrair texto
            texto = self.extrair_texto(imagem_bytes)

            if not texto or len(texto.strip()) < 20:
                return {
                    'sucesso': False,
                    'erro': 'Não foi possível extrair texto da imagem',
                    'sugestao': 'Tente tirar uma foto mais nítida da nota fiscal'
                }

            # Identificar supermercado
            supermercado = self.identificar_supermercado(texto)

            # Extrair data
            data_compra = self.extrair_data(texto)

            # Extrair produtos
            produtos = self.extrair_produtos(texto)

            if not produtos:
                return {
                    'sucesso': False,
                    'erro': 'Não foi possível identificar produtos na nota fiscal',
                    'texto_extraido': texto[:500],
                    'sugestao': 'Certifique-se de que a nota fiscal está completa e legível'
                }

            # Extrair total
            total = self.extrair_total(texto)

            # Validar total com soma dos produtos
            soma_produtos = sum(p['preco'] * p['quantidade'] for p in produtos)

            # Se o total bate (com margem de 5%), marcar como verificado
            verificado = False
            if total:
                diferenca_percentual = abs(total - soma_produtos) / total * 100
                verificado = diferenca_percentual < 5

            return {
                'sucesso': True,
                'supermercado': supermercado or 'Não identificado',
                'data_compra': data_compra.isoformat() if data_compra else None,
                'produtos': produtos,
                'total_produtos': len(produtos),
                'total_nota': total,
                'soma_produtos': round(soma_produtos, 2),
                'verificado': verificado,
                'texto_completo': texto,
                'confianca': self._calcular_confianca(produtos, total, soma_produtos)
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def _calcular_confianca(self, produtos: List[Dict], total: Optional[float], soma: float) -> float:
        """Calcula nível de confiança da extração (0-100%)"""
        confianca = 50.0  # Base

        # Aumentar se encontrou produtos
        if produtos:
            confianca += 20

            # Mais produtos = mais confiança
            if len(produtos) >= 5:
                confianca += 10

            # Se total bate com soma
            if total and abs(total - soma) / total < 0.05:
                confianca += 20

        return min(confianca, 100.0)


# Instância global
_ocr_instance = None

def get_ocr_nota_fiscal() -> NotaFiscalOCR:
    """Obtém instância singleton do OCR de nota fiscal"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = NotaFiscalOCR()
    return _ocr_instance
