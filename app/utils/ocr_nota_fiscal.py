"""
OCR para Notas Fiscais de Supermercado
Reconhece e extrai produtos e preços de cupons fiscais
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
import pytesseract
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io
from difflib import SequenceMatcher
import numpy as np


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

        # DICIONÁRIO DE PRODUTOS COMUNS (para correção de OCR)
        # Produtos mais comuns em supermercados brasileiros
        self.produtos_comuns = [
            # Grãos e cereais
            'ARROZ', 'FEIJAO', 'FEIJÃO', 'MACARRAO', 'MACARRÃO', 'FARINHA', 'FUBÁ', 'FUBA',
            'AVEIA', 'GRANOLA', 'QUINOA',

            # Bebidas
            'CAFE', 'CAFÉ', 'CHA', 'CHÁ', 'SUCO', 'REFRIGERANTE', 'AGUA', 'ÁGUA',
            'CERVEJA', 'VINHO', 'LEITE', 'IOGURTE', 'ACHOCOLATADO',

            # Frutas e verduras
            'BANANA', 'MACA', 'MAÇÃ', 'LARANJA', 'LIMAO', 'LIMÃO', 'MELAO', 'MELÃO',
            'MELANCIA', 'MAMAO', 'MAMÃO', 'MORANGO', 'UVA', 'PERA', 'ABACAXI',
            'TOMATE', 'CEBOLA', 'ALHO', 'BATATA', 'CENOURA', 'ALFACE', 'REPOLHO',
            'BROCOLIS', 'BRÓCOLIS', 'COUVE', 'PEPINO', 'PIMENTAO', 'PIMENTÃO',

            # Carnes e proteínas
            'CARNE', 'FRANGO', 'PEIXE', 'LINGUICA', 'LINGUIÇA', 'SALSICHA', 'BACON',
            'PRESUNTO', 'MORTADELA', 'SALAME', 'OVO', 'OVOS',

            # Laticínios
            'QUEIJO', 'MANTEIGA', 'MARGARINA', 'REQUEIJAO', 'REQUEIJÃO', 'CREAM CHEESE',

            # Condimentos e temperos
            'SAL', 'PIMENTA', 'OLEO', 'ÓLEO', 'AZEITE', 'VINAGRE', 'MOLHO', 'CATCHUP',
            'KETCHUP', 'MAIONESE', 'MOSTARDA',

            # Produtos de limpeza
            'SABAO', 'SABÃO', 'DETERGENTE', 'AMACIANTE', 'DESINFETANTE', 'AGUA SANITARIA',
            'ALVEJANTE', 'ESPONJA', 'PAPEL HIGIENICO', 'PAPEL HIGIÊNICO',

            # Higiene pessoal
            'SHAMPOO', 'CONDICIONADOR', 'SABONETE', 'PASTA DE DENTE', 'CREME DENTAL',
            'DESODORANTE', 'ABSORVENTE',

            # Outros
            'ACUCAR', 'AÇÚCAR', 'BISCOITO', 'BOLACHA', 'PÃO', 'PAO', 'BOLO', 'CHOCOLATE',
            'SORVETE', 'PIRAO', 'PIRÃO', 'SARDINHA', 'ATUM'
        ]

        # Converter para maiúsculas para comparação
        self.produtos_comuns_upper = [p.upper() for p in self.produtos_comuns]

    def extrair_texto(self, imagem_bytes: bytes) -> str:
        """Extrai texto da imagem da nota fiscal - SUPER OTIMIZADO para fotos do WhatsApp"""
        try:
            imagem = Image.open(io.BytesIO(imagem_bytes))

            print(f"Imagem original: {imagem.width}x{imagem.height}, modo: {imagem.mode}")

            # ESTRATÉGIA PARA FOTOS DO WHATSAPP (comprimidas, baixa qualidade):
            # 1. Manter tamanho razoável (não muito pequeno)
            # 2. Aplicar pré-processamento MODERADO
            # 3. NÃO exagerar no processamento (pode piorar)

            # Tamanho ideal: 1200px (bom balanço)
            target_dimension = 1200

            # Calcular novo tamanho mantendo proporção
            if imagem.width > imagem.height:
                if imagem.width > target_dimension:
                    ratio = target_dimension / imagem.width
                    new_width = target_dimension
                    new_height = int(imagem.height * ratio)
                else:
                    new_width, new_height = imagem.width, imagem.height
            else:
                if imagem.height > target_dimension:
                    ratio = target_dimension / imagem.height
                    new_height = target_dimension
                    new_width = int(imagem.width * ratio)
                else:
                    new_width, new_height = imagem.width, imagem.height

            # Redimensionar se necessário
            if (new_width, new_height) != (imagem.width, imagem.height):
                # LANCZOS = melhor qualidade para redução
                imagem = imagem.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"Redimensionada para: {new_width}x{new_height}")

            # PRÉ-PROCESSAMENTO SIMPLES (menos processamento = melhor resultado)

            # 1. Converter para RGB se necessário
            if imagem.mode != 'RGB':
                imagem = imagem.convert('RGB')

            # 2. Aumentar contraste moderadamente
            enhancer = ImageEnhance.Contrast(imagem)
            imagem = enhancer.enhance(2.0)

            # 3. Aumentar nitidez moderadamente
            enhancer = ImageEnhance.Sharpness(imagem)
            imagem = enhancer.enhance(2.0)

            # 4. Converter para escala de cinza
            imagem = imagem.convert('L')

            print(f"Pré-processamento completo. Iniciando OCR...")

            # Configuração do Tesseract
            # PSM 6 = bloco uniforme de texto
            # OEM 3 = LSTM + Legacy (melhor para textos mistos)
            custom_config = r'--oem 3 --psm 6 -l por'

            # TIMEOUT: 120 segundos
            texto = pytesseract.image_to_string(imagem, config=custom_config, timeout=120)

            print(f"OCR concluído. {len(texto)} caracteres extraídos")

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

        # Se não encontrou no formato multilinha, tentar linha única
        # FORMATO REAL das notas fiscais brasileiras (tudo em 1 linha):
        # 004 14519 ACEM BOVINO SEM OSSO ... 0,320KG 34,99 11,20
        # ↑   ↑     ↑ NOME DO PRODUTO      ↑qtd    ↑preço/kg ↑total

        padroes = [
            # Padrão 1: num_item codigo_produto NOME quantidade unidade preço_unit preço_total
            # Ex: 004 14519 ACEM BOVINO SEM OSSO 0,320KG 34,99 11,20
            r'^(\d{2,4})\s+(\d{4,13})\s+(.+?)\s+(\d+[.,]\d+)\s*(KG|UN|LT|L|G|ML|PC|PCT|CX)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})',

            # Padrão 2: num_item NOME quantidade unidade preço_unit preço_total (sem código)
            r'^(\d{2,4})\s+([A-Z].+?)\s+(\d+[.,]\d+)\s*(KG|UN|LT|L|G|ML|PC|PCT|CX)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})',

            # Padrão 3: num_item codigo NOME preço total (2 preços no final, FLEXÍVEL)
            # Ex: 004 14519 ACEM BOVINO SEM OSSO 34,99 11,20  (OCR errou, sem qtd/unidade)
            r'^(\d{2,4})\s+(\d{4,13})\s+(.+?)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})\s*$',

            # Padrão 4: num_item codigo NOME preço (sem quantidade explícita)
            r'^(\d{2,4})\s+(\d{4,13})\s+(.+?)\s+(\d+[.,]\d{2})\s*$',
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
                        if i == 0:  # Padrão 1: num codigo NOME qtd unidade preço_unit total
                            # grupos: (num, codigo, nome, qtd, unidade, preço_unit, total)
                            num_item = grupos[0]
                            codigo = grupos[1]  # Ignorar
                            nome_produto = grupos[2].strip()
                            quantidade_str = grupos[3].replace(',', '.')
                            unidade = grupos[4].upper()
                            preco_unit_str = grupos[5].replace(',', '.')
                            total_str = grupos[6].replace(',', '.')

                            quantidade = float(quantidade_str)
                            preco_unitario = float(preco_unit_str)
                            total = float(total_str)

                        elif i == 1:  # Padrão 2: num NOME qtd unidade preço_unit total (sem código)
                            # grupos: (num, nome, qtd, unidade, preço_unit, total)
                            num_item = grupos[0]
                            nome_produto = grupos[1].strip()
                            quantidade_str = grupos[2].replace(',', '.')
                            unidade = grupos[3].upper()
                            preco_unit_str = grupos[4].replace(',', '.')
                            total_str = grupos[5].replace(',', '.')

                            quantidade = float(quantidade_str)
                            preco_unitario = float(preco_unit_str)
                            total = float(total_str)

                        elif i == 2:  # Padrão 3: num codigo NOME preço_unit total (2 preços)
                            # grupos: (num, codigo, nome, preço_unit, total)
                            num_item = grupos[0]
                            codigo = grupos[1]  # Ignorar
                            nome_produto = grupos[2].strip()
                            preco_unitario = float(grupos[3].replace(',', '.'))
                            total = float(grupos[4].replace(',', '.'))
                            quantidade = 1.0  # Assume 1 unidade
                            unidade = 'UN'

                        elif i == 3:  # Padrão 4: num codigo NOME preço
                            # grupos: (num, codigo, nome, preço)
                            num_item = grupos[0]
                            codigo = grupos[1]  # Ignorar
                            nome_produto = grupos[2].strip()
                            preco_unitario = float(grupos[3].replace(',', '.'))
                            quantidade = 1.0
                            unidade = 'UN'
                            total = preco_unitario

                        else:
                            continue

                        # LIMPEZA SUPER AGRESSIVA DE CÓDIGOS E PREÇOS (mesma lógica do multilinha)
                        # Passo 1: Remover preços no final (formato: 34,99 ou 11,20 ou 40.890)
                        nome_produto = re.sub(r'\s+\d+[.,]\d+(\s+\d+[.,]\d+)*\s*$', '', nome_produto)

                        # Passo 2: Remover quantidade+unidade no final (ex: 0,320KG, 1,565Kg)
                        nome_produto = re.sub(r'\s+\d+[.,]\d+\s*(?:KG|K6|G|LT|L|ML|UN|PC|PCT|CX)\s*$', '', nome_produto, flags=re.IGNORECASE)

                        # Passo 3: Remover códigos NO INÍCIO
                        nome_produto = re.sub(r'^\d{4,}\s+', '', nome_produto)

                        # Passo 4: Remover códigos EAN/GTIN (7-13 dígitos)
                        nome_produto = re.sub(r'\b\d{7,13}\b', '', nome_produto)

                        # Passo 5: Remover códigos SKU/internos (4-6 dígitos), mas não números do nome
                        nome_produto = re.sub(r'\b\d{4,6}\b(?!\s*(?:GR|G|ML|L|KG|PODERES|,))', '', nome_produto)

                        # Passo 6: Remover códigos de barras longos
                        nome_produto = re.sub(r'\b\d{10,}\w*\b', '', nome_produto)

                        # Passo 7: Remover números grandes (códigos/preços como 40.890, 25:24)
                        nome_produto = re.sub(r'\b\d{2,}[.,:]\d{2,}\b', '', nome_produto)

                        # Passo 8: Remover letras isoladas no final (OCR ruim: Ee, O, L, etc)
                        nome_produto = re.sub(r'\s+[A-Z]{1,2}(?:\s+[A-Z]{1,2})*\s*$', '', nome_produto)

                        # Passo 9: Remover especificações de peso/medida DEPOIS do nome
                        # Ex: "CAFE 3 PODERES 250G EXTRAFORTE" -> "CAFE 3 PODERES"
                        nome_produto = re.sub(r'\s+\d+[.,]?\d*\s*(?:G|GR|KG|K6|ML|L|LT)(?:\s+\w+)*\s*$', '', nome_produto, flags=re.IGNORECASE)

                        # Passo 10: Limpar sufixos comuns de tipo/unidade
                        sufixos_remover = [
                            'KG', 'K6', 'UN', 'LT', 'L', 'ML', 'G', 'GR', 'PC', 'PCT', 'CX', 'EMB', 'PACOTE',
                            'RESF', 'CONG', 'CONGEL', 'RESFR', 'RESP', 'CON', 'POTA',
                            'BDJ', 'GRILO', 'MG', 'GO', 'CUBOS', 'PEDACO', 'TRAZ', 'CORTADA',
                            'GU', 'UND', 'COMUM', 'VERDE', 'SEMENTE', 'EDU', 'OL', 'PETA',
                            'UNO', 'TRAD', 'BANO', 'Bnd', 'BD', 'NUR', 'RES', 'RR', 'EE',
                            'FRIATO', 'SOBRECOKA', 'PETS', 'UERDE', 'DSSO', 'EXTRAFORTE', 'EXTRA',
                            'TRADICIONAL', 'SUAVE', 'FORTE', 'LEVE', 'DIET', 'LIGHT', 'ZERO'
                        ]
                        padrao_sufixos = r'\s+(' + '|'.join(sufixos_remover) + r')(\s+(' + '|'.join(sufixos_remover) + r'))*\s*$'
                        nome_produto = re.sub(padrao_sufixos, '', nome_produto, flags=re.IGNORECASE)

                        # Passo 10: Limpar caracteres estranhos
                        nome_produto = re.sub(r'[_\-]{2,}', ' ', nome_produto)
                        nome_produto = re.sub(r'\s+', ' ', nome_produto)
                        nome_produto = nome_produto.strip()

                        # Passo 11: Limpar código inicial se tiver
                        nome_produto = re.sub(r'^\d+\s+', '', nome_produto)
                        nome_produto = re.sub(r'\s+\d+$', '', nome_produto)

                        # Passo 12: Remover símbolos estranhos
                        nome_produto = re.sub(r'[\*\+\|»\!]', '', nome_produto)

                        # Passo 13: Limpar caracteres especiais e pontuação
                        nome_produto = re.sub(r'^["\'\—\-\s\+\*\!]+', '', nome_produto)
                        nome_produto = re.sub(r'["\'\—\-\s\+\*\!]+$', '', nome_produto)
                        nome_produto = re.sub(r'\s+', ' ', nome_produto)
                        nome_produto = nome_produto.strip()

                        # Validações rigorosas
                        nome_valido = len(nome_produto) >= 3 and not nome_produto.replace(' ', '').isdigit()

                        # Preço unitário razoável
                        preco_valido = 0.10 < preco_unitario < 500

                        # Quantidade razoável (depende da unidade)
                        if i < 2:  # Padrões 1 e 2 têm unidade
                            if unidade in ['KG', 'G', 'LT', 'L', 'ML']:
                                qtd_valida = 0.001 < quantidade <= 50
                            else:
                                qtd_valida = 0 < quantidade <= 100
                        else:
                            qtd_valida = True

                        # Total razoável
                        total_valido = total < 500

                        if nome_valido and preco_valido and qtd_valida and total_valido:
                            produtos.append({
                                'nome': nome_produto.title(),
                                'preco': preco_unitario,
                                'quantidade': quantidade if i < 2 else 1.0,
                                'unidade': unidade if i < 2 else 'UN'
                            })
                            produto_encontrado = True
                            break

                    except (ValueError, IndexError):
                        continue

        return produtos

    def _extrair_produtos_multilinhas(self, linhas: List[str], palavras_ignorar: List[str]) -> List[Dict]:
        """
        Extrai produtos de notas onde produto e preço estão em linhas separadas

        Formato moderno de nota fiscal brasileira (2025):

        CABEÇALHO (detectar primeiro):
        CODIGO DESCRIÇÃO QTDE UN VL TOTAL

        Depois vem os produtos:
        Linha 1: 002 12556 FILE PEITO SUPER FRANGO Kg RESF
                 ↑   ↑     ↑ NOME DO PRODUTO
                 |   └─────── código do produto (EAN/SKU) - REMOVER
                 └─────────── número do item - REMOVER

        Linha 2: 1,565Kg 19,98  36,06
                 ↑       ↑      ↑
                 |       |      └─── total (ignorar)
                 |       └────────── preço unitário (usar)
                 └────────────────── quantidade

        Estratégia:
        1. Encontrar linha com cabeçalho (CODIGO, DESCRIÇÃO, QTDE, etc)
        2. Extrair produtos APENAS depois do cabeçalho
        """
        produtos = []
        i = 0

        # PASSO 1: Encontrar o início da lista de produtos (linha de cabeçalho)
        inicio_produtos = 0
        for idx, linha in enumerate(linhas):
            linha_upper = linha.upper()
            # Detectar cabeçalho: deve ter pelo menos 2 dessas palavras
            palavras_cabecalho = ['CODIGO', 'DESCRICAO', 'QTDE', 'TOTAL', 'VL', 'UN']
            contagem = sum(1 for palavra in palavras_cabecalho if palavra in linha_upper)

            if contagem >= 2:
                inicio_produtos = idx + 1  # Produtos começam na linha seguinte
                print(f"DEBUG - Cabeçalho encontrado na linha {idx}: '{linha}'")
                print(f"DEBUG - Produtos começam na linha {inicio_produtos}")
                break

        # Se não encontrou cabeçalho, começa do início
        if inicio_produtos == 0:
            print("DEBUG - Cabeçalho não encontrado, processando desde o início")

        i = inicio_produtos

        while i < len(linhas) - 1:
            linha_atual = linhas[i].strip()
            linha_seguinte = linhas[i + 1].strip()

            # Pular linhas vazias
            if not linha_atual or not linha_seguinte:
                i += 1
                continue

            # PARAR se encontrar indicadores de fim da lista de produtos
            palavras_fim = ['SUBTOTAL', 'TOTAL GERAL', 'FORMA DE PAGAMENTO', 'DINHEIRO',
                           'CARTAO', 'TROCO', 'VALOR PAGO', 'DESCONTO']
            linha_upper = linha_atual.upper()
            if any(palavra in linha_upper for palavra in palavras_fim):
                print(f"DEBUG - Fim da lista de produtos detectado: '{linha_atual}'")
                break

            # Pular se tem palavras-chave a ignorar
            if any(palavra in linha_atual.upper() for palavra in palavras_ignorar):
                i += 1
                continue

            # ESTRATÉGIA SUPER MELHORADA: Buscar APENAS LETRAS após TODOS os números
            #
            # LINHA 1: numero_item codigo_produto NOME_PRODUTO especificações
            # Exemplo: 006 789 MERANTE SUKITA 21 LARA UA
            #          ↑   ↑   ↑ NOME (queremos apenas MERANTE SUKITA)
            #          |   └─── código (pode ter espaços: 789, 7891, etc)
            #          └─────── número do item
            #
            # Estratégia:
            # 1. Remover TODOS os números e espaços do INÍCIO
            # 2. Capturar primeira sequência de PALAVRAS (letras)
            # 3. Parar antes de números+unidade (250G, 2L, etc)

            nome_produto = None

            # NOVO REGEX: Remove TUDO que não é letra no início, pega só letras/espaços
            # Exemplo: "006 789 MERANTE SUKITA 21 LARA" -> captura "MERANTE SUKITA"
            #          "04 2667 FILE PEITO SUPER FRANGO" -> captura "FILE PEITO SUPER FRANGO"

            # Passo 1: Remover números e espaços do início
            linha_limpa = re.sub(r'^[\d\s]+', '', linha_atual)

            # Passo 2: Capturar apenas letras e espaços (nome), parar em número isolado ou especificação
            match_nome = re.search(r'^([A-ZÇÁÉÍÓÚÀÃÕÂÊÔ][A-ZÇÁÉÍÓÚÀÃÕÂÊÔ\s]+?)(?:\s+\d+|\s+ka|\s+kg|\s+[A-Z]{1,2}\s*$|$)', linha_limpa, re.IGNORECASE)

            if match_nome:
                nome_produto = match_nome.group(1).strip()
                print(f"DEBUG - Nome extraído: '{linha_atual}' -> linha limpa: '{linha_limpa}' -> nome: '{nome_produto}'")

            if nome_produto:
                # LIMPEZA SIMPLIFICADA (já capturamos só o essencial)

                # Passo 1: Remover qualquer número de 4+ dígitos (códigos restantes)
                nome_produto = re.sub(r'\b\d{4,}\b', '', nome_produto)

                # Passo 2: Remover sufixos de especificação/unidade comuns
                sufixos_remover = [
                    'KG', 'K6', 'UN', 'LT', 'L', 'ML', 'G', 'GR', 'PC', 'PCT', 'CX', 'EMB',
                    'RESF', 'CONG', 'CONGEL', 'RESFR', 'RESP', 'CON',
                    'GU', 'GO', 'MG', 'EDU', 'OL', 'NUR', 'RES', 'RR', 'EE', 'Ee',
                    'FRIATO', 'PETS', 'UERDE', 'DSSO', 'SOBRECOKA'
                ]
                padrao_sufixos = r'\s+(' + '|'.join(sufixos_remover) + r')(\s+(' + '|'.join(sufixos_remover) + r'))*\s*$'
                nome_produto = re.sub(padrao_sufixos, '', nome_produto, flags=re.IGNORECASE)

                # Passo 3: Remover símbolos e pontuação estranha
                nome_produto = re.sub(r'[\*\+\|»\!]', '', nome_produto)

                # Passo 4: Limpar espaços múltiplos
                nome_produto = re.sub(r'\s+', ' ', nome_produto).strip()

                print(f"DEBUG - Nome após limpeza: '{nome_produto}'")

                # LINHA 2: Quantidade + Unidade + Preço Unitário + Total
                # Objetivo: Extrair apenas QUANTIDADE e PREÇO (ignorar resto)
                #
                # Exemplos:
                # 1UN 12,97 12,97  → qtd=1, unidade=UN, preço=12,97
                # 1,565KG 19,98 37,06  → qtd=1.565, unidade=KG, preço=19,98
                # 2 5,50 11,00  → qtd=2, unidade=UN, preço=5,50
                #
                # Estratégia: buscar PRIMEIRO número (quantidade) e PRIMEIRO preço (formato X,XX)

                padroes_preco = [
                    # Padrão 1: quantidade + unidade + preço + total
                    # Ex: 1UN 12,97 12,97 ou 1,565KG 19,98 37,06
                    r'^\s*(\d+[.,]?\d*)\s*(KG|K6|UN|LT|L|ML|G|PC|PCT|CX|JUN)?\s+(\d+[.,]\d{2})',

                    # Padrão 2: apenas quantidade e preço (sem unidade)
                    # Ex: 2 5,50 11,00
                    r'^\s*(\d+[.,]?\d*)\s+(\d+[.,]\d{2})',
                ]

                for idx_padrao, padrao_preco in enumerate(padroes_preco):
                    match_preco = re.search(padrao_preco, linha_seguinte, re.IGNORECASE)

                    if match_preco:
                        try:
                            grupos = match_preco.groups()

                            # Extrair quantidade
                            quantidade_str = grupos[0].replace(',', '.')
                            quantidade = float(quantidade_str)

                            # Extrair unidade (se existir)
                            if idx_padrao == 0 and len(grupos) >= 3:
                                # Padrão 1: tem unidade
                                unidade = (grupos[1] or 'UN').upper().replace('JUN', 'UN')
                                preco_str = grupos[2].replace(',', '.')
                            else:
                                # Padrão 2: sem unidade
                                unidade = 'UN'
                                preco_str = grupos[1].replace(',', '.')

                            # Pegar APENAS o primeiro preço (ignorar total)
                            preco_unitario = float(preco_str)

                            print(f"DEBUG - Linha 2: '{linha_seguinte}' -> qtd={quantidade}, unidade={unidade}, preço={preco_unitario}")

                            # Validações simples
                            nome_valido = len(nome_produto) >= 3 and not nome_produto.replace(' ', '').isdigit()
                            preco_valido = 0.10 < preco_unitario < 1000
                            qtd_valida = 0 < quantidade <= 100

                            if nome_valido and preco_valido and qtd_valida:
                                # 🤖 CORREÇÃO INTELIGENTE: Corrigir erros de OCR no nome
                                nome_corrigido = self.corrigir_palavras_no_nome(nome_produto)

                                produtos.append({
                                    'nome': nome_corrigido.title(),
                                    'preco': preco_unitario,  # preço unitário (por kg ou por unidade)
                                    'quantidade': quantidade,
                                    'unidade': unidade  # adicionar unidade para referência
                                })

                                i += 2  # Pula as duas linhas processadas
                                break  # Sai do loop de padrões

                        except (ValueError, IndexError):
                            continue

            i += 1

        return produtos

    def corrigir_nome_produto_com_ia(self, nome_ocr: str) -> str:
        """
        Corrige erros de OCR no nome do produto usando similaridade de strings

        Exemplos:
        - "CARE" -> "CAFE" (similaridade 75%)
        - "NELAO" -> "MELAO" (similaridade 80%)
        - "RARINHA" -> "FARINHA" (similaridade 85%)
        """
        nome_upper = nome_ocr.upper().strip()

        # Se for muito curto, não tentar corrigir
        if len(nome_upper) < 3:
            return nome_ocr

        # Se já existe exatamente no dicionário, retornar original
        if nome_upper in self.produtos_comuns_upper:
            return nome_ocr

        # Procurar produto similar no dicionário
        melhor_match = None
        melhor_similaridade = 0.0
        THRESHOLD = 0.75  # 75% de similaridade mínima

        for produto_conhecido in self.produtos_comuns_upper:
            # Calcular similaridade usando SequenceMatcher
            similaridade = SequenceMatcher(None, nome_upper, produto_conhecido).ratio()

            if similaridade > melhor_similaridade and similaridade >= THRESHOLD:
                melhor_similaridade = similaridade
                melhor_match = produto_conhecido

        # Se encontrou um match bom, usar correção
        if melhor_match and melhor_similaridade >= THRESHOLD:
            print(f"🤖 CORREÇÃO OCR: '{nome_ocr}' -> '{melhor_match}' (similaridade: {melhor_similaridade:.0%})")
            return melhor_match

        # Se não encontrou nada similar, retornar original
        return nome_ocr

    def corrigir_palavras_no_nome(self, nome: str) -> str:
        """
        Corrige palavra por palavra no nome do produto

        Exemplo: "CARE COM ACUCAR" -> "CAFE COM AÇUCAR"
        """
        palavras = nome.split()
        palavras_corrigidas = []

        for palavra in palavras:
            # Pular palavras muito curtas (preposições, etc)
            if len(palavra) <= 2:
                palavras_corrigidas.append(palavra)
                continue

            # Tentar corrigir a palavra
            palavra_corrigida = self.corrigir_nome_produto_com_ia(palavra)
            palavras_corrigidas.append(palavra_corrigida)

        return ' '.join(palavras_corrigidas)

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
