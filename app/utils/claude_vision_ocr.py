"""
OCR usando Claude Vision API da Anthropic
Sistema muito mais preciso para ler notas fiscais do que Tesseract
"""
import base64
import os
from typing import List, Dict, Optional
from datetime import datetime
import anthropic
from anthropic import Anthropic
import json


class ClaudeVisionOCR:
    """OCR usando Claude Vision API para notas fiscais"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o OCR com Claude Vision

        Args:
            api_key: Chave da API Anthropic (ou usa variável de ambiente ANTHROPIC_API_KEY)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY não encontrada. "
                "Configure a variável de ambiente ou passe a chave no construtor."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Melhor modelo com visão

    def extrair_produtos_nota_fiscal(
        self,
        imagem_bytes: bytes,
        formato_imagem: str = "image/jpeg"
    ) -> Dict:
        """
        Extrai produtos e informações de uma nota fiscal usando Claude Vision

        Args:
            imagem_bytes: Bytes da imagem da nota fiscal
            formato_imagem: Formato da imagem (image/jpeg, image/png, etc)

        Returns:
            Dict com: supermercado, data, produtos[], total, cnpj, endereco
        """

        # Converter imagem para base64
        imagem_base64 = base64.standard_b64encode(imagem_bytes).decode('utf-8')

        # Prompt especializado para extrair informações da nota fiscal
        prompt = """Você é um especialista em ler notas fiscais de supermercados brasileiros.

Analise esta imagem de nota fiscal e extraia as seguintes informações em formato JSON:

{
  "supermercado": "nome do supermercado",
  "cnpj": "CNPJ do estabelecimento (se encontrar)",
  "endereco": "endereço completo do estabelecimento",
  "data_compra": "data da compra no formato YYYY-MM-DD",
  "hora_compra": "hora da compra no formato HH:MM:SS",
  "produtos": [
    {
      "codigo": "código do produto (se houver)",
      "nome": "nome do produto (limpo e corrigido)",
      "quantidade": "quantidade comprada",
      "unidade": "unidade (kg, un, lt, etc)",
      "preco_unitario": preço unitário em decimal,
      "preco_total": preço total em decimal
    }
  ],
  "subtotal": valor do subtotal em decimal,
  "descontos": valor de descontos em decimal,
  "total": valor total em decimal,
  "forma_pagamento": "forma de pagamento (débito, crédito, dinheiro, pix)"
}

IMPORTANTE:
1. Limpe os nomes dos produtos (remova códigos, asteriscos, etc)
2. Corrija erros de OCR em nomes de produtos conhecidos
3. Extraia TODOS os produtos da nota, não apenas alguns
4. Se não conseguir identificar algum campo, use null
5. Preços devem ser números decimais (exemplo: 19.98, não "19,98")
6. Para quantidade, extraia o peso/unidades do produto
7. Retorne APENAS o JSON, sem texto adicional antes ou depois

Seja preciso e extraia o máximo de informações possível da nota fiscal."""

        try:
            # Fazer requisição para Claude com a imagem
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": formato_imagem,
                                    "data": imagem_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Extrair resposta
            resposta_texto = message.content[0].text

            # Limpar resposta (remover markdown se houver)
            resposta_texto = resposta_texto.strip()
            if resposta_texto.startswith('```json'):
                resposta_texto = resposta_texto[7:]
            if resposta_texto.startswith('```'):
                resposta_texto = resposta_texto[3:]
            if resposta_texto.endswith('```'):
                resposta_texto = resposta_texto[:-3]
            resposta_texto = resposta_texto.strip()

            # Parse JSON
            dados = json.loads(resposta_texto)

            # Adicionar metadados
            dados['metadados'] = {
                'modelo': self.model,
                'tokens_usados': message.usage.input_tokens + message.usage.output_tokens,
                'data_extracao': datetime.now().isoformat(),
                'sucesso': True
            }

            return dados

        except json.JSONDecodeError as e:
            # Se falhar o parse JSON, retornar erro com resposta bruta
            return {
                'sucesso': False,
                'erro': f'Erro ao parsear JSON: {str(e)}',
                'resposta_bruta': resposta_texto if 'resposta_texto' in locals() else None,
                'metadados': {
                    'modelo': self.model,
                    'data_extracao': datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'metadados': {
                    'modelo': self.model,
                    'data_extracao': datetime.now().isoformat()
                }
            }

    def validar_e_corrigir_produtos(self, produtos: List[Dict]) -> List[Dict]:
        """
        Valida e corrige dados dos produtos extraídos

        Args:
            produtos: Lista de produtos extraídos

        Returns:
            Lista de produtos validados e corrigidos
        """
        produtos_validos = []

        for produto in produtos:
            # Validar campos obrigatórios
            if not produto.get('nome'):
                continue

            # Limpar nome do produto
            nome = produto['nome'].strip()
            nome = ' '.join(nome.split())  # Remover espaços duplos

            # Validar e corrigir preços
            try:
                preco_total = float(produto.get('preco_total', 0))
                if preco_total <= 0:
                    continue  # Ignorar produtos sem preço
            except (ValueError, TypeError):
                continue

            # Criar produto validado
            produto_valido = {
                'nome': nome,
                'preco': preco_total,
                'quantidade': produto.get('quantidade', '1'),
                'unidade': produto.get('unidade', 'un'),
                'codigo': produto.get('codigo'),
                'preco_unitario': produto.get('preco_unitario', preco_total)
            }

            produtos_validos.append(produto_valido)

        return produtos_validos


def get_claude_vision_ocr() -> ClaudeVisionOCR:
    """Factory function para criar instância do OCR"""
    return ClaudeVisionOCR()
