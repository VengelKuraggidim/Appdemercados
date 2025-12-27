"""
Servico de busca de produtos por codigo de barras EAN
Integra com Open Food Facts API e outras fontes
"""
import requests
from typing import Optional, Dict


class EANService:
    """Servico para buscar produtos por codigo de barras EAN"""

    # Open Food Facts API (gratuita, sem chave)
    OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v0/product/{ean}.json"

    # Cosmos API (brasileira, requer chave)
    COSMOS_URL = "https://api.cosmos.bluesoft.com.br/gtins/{ean}"

    def __init__(self, cosmos_api_key: Optional[str] = None):
        self.cosmos_api_key = cosmos_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AppDeMercados/1.0 (Comparador de Precos)'
        })

    def buscar_por_ean(self, ean: str) -> Optional[Dict]:
        """
        Busca produto por codigo de barras EAN.
        Tenta Open Food Facts primeiro, depois Cosmos se disponivel.
        """
        # Limpa EAN (remove espacos, zeros a esquerda)
        ean = ean.strip()
        if len(ean) < 8:
            return None

        # Normaliza para 13 digitos se necessario
        if len(ean) < 13:
            ean = ean.zfill(13)

        # Tenta Open Food Facts primeiro (gratuito)
        resultado = self._buscar_open_food_facts(ean)
        if resultado:
            return resultado

        # Tenta Cosmos se API key disponivel
        if self.cosmos_api_key:
            resultado = self._buscar_cosmos(ean)
            if resultado:
                return resultado

        return None

    def _buscar_open_food_facts(self, ean: str) -> Optional[Dict]:
        """Busca na API Open Food Facts"""
        try:
            url = self.OPEN_FOOD_FACTS_URL.format(ean=ean)
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()

            if data.get('status') != 1:
                return None

            product = data.get('product', {})

            # Extrai nome em portugues ou generico
            nome = (
                product.get('product_name_pt') or
                product.get('product_name_pt-BR') or
                product.get('product_name') or
                'Produto'
            )

            # Extrai marca
            marcas = product.get('brands', '')
            marca = marcas.split(',')[0].strip() if marcas else None

            # Extrai categoria
            categorias = product.get('categories', '')
            categoria = categorias.split(',')[0].strip() if categorias else None

            return {
                'ean': ean,
                'nome': nome,
                'marca': marca,
                'categoria': categoria,
                'imagem_url': product.get('image_url'),
                'imagem_thumb': product.get('image_thumb_url'),
                'ingredientes': product.get('ingredients_text_pt') or product.get('ingredients_text'),
                'nutriscore': product.get('nutriscore_grade'),
                'fonte': 'open_food_facts'
            }

        except Exception as e:
            print(f"Erro ao buscar Open Food Facts: {e}")
            return None

    def _buscar_cosmos(self, ean: str) -> Optional[Dict]:
        """Busca na API Cosmos (produtos brasileiros)"""
        try:
            url = self.COSMOS_URL.format(ean=ean)
            headers = {
                'X-Cosmos-Token': self.cosmos_api_key,
                'User-Agent': 'AppDeMercados/1.0'
            }

            response = self.session.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()

            return {
                'ean': ean,
                'nome': data.get('description', 'Produto'),
                'marca': data.get('brand', {}).get('name'),
                'categoria': data.get('ncm', {}).get('full_description'),
                'imagem_url': data.get('thumbnail'),
                'preco_medio': data.get('avg_price'),
                'fonte': 'cosmos'
            }

        except Exception as e:
            print(f"Erro ao buscar Cosmos: {e}")
            return None

    def extrair_ean_de_imagem(self, image_data: bytes) -> Optional[str]:
        """
        Extrai codigo de barras de uma imagem usando pyzbar.
        Retorna o EAN encontrado ou None.
        """
        try:
            from pyzbar import pyzbar
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_data))
            barcodes = pyzbar.decode(image)

            if not barcodes:
                return None

            # Retorna o primeiro codigo de barras encontrado
            for barcode in barcodes:
                if barcode.type in ['EAN13', 'EAN8', 'UPCA', 'UPCE', 'CODE128']:
                    return barcode.data.decode('utf-8')

            return None

        except ImportError:
            print("pyzbar nao instalado. Execute: pip install pyzbar")
            return None
        except Exception as e:
            print(f"Erro ao extrair EAN da imagem: {e}")
            return None


# Instancia global
ean_service = EANService()
