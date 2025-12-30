"""
Sistema Híbrido Inteligente de OCR
Combina EasyOCR (grátis) + Google Vision + Claude Vision
Escolhe automaticamente o melhor baseado em custo x precisão
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class OCREngine(Enum):
    """Engines de OCR disponíveis"""
    EASYOCR = "easyocr"  # Grátis, offline, precisão ~70%
    GOOGLE_VISION = "google_vision"  # 1000/mês grátis, precisão ~90%
    CLAUDE_VISION = "claude_vision"  # Pago, precisão ~99%


class OCRHibrido:
    """Sistema inteligente que escolhe o melhor OCR automaticamente"""

    def __init__(self):
        """Inicializa o sistema híbrido"""
        self.tentativas = []
        self.confianca_minima_easyocr = 70.0  # Se < 70%, tenta próximo nível
        self.produtos_minimos = 5  # Mínimo de produtos esperado

    def processar_nota_fiscal(
        self,
        imagem_bytes: bytes,
        usuario_prefere_gratis: bool = True,
        usuario_tem_creditos_api: bool = False,
        modo_forcado: Optional[str] = None
    ) -> Dict:
        """
        Processa nota fiscal escolhendo automaticamente o melhor OCR

        Args:
            imagem_bytes: Bytes da imagem
            usuario_prefere_gratis: Se True, prioriza engines gratuitos
            usuario_tem_creditos_api: Se usuário tem créditos Claude/Google
            modo_forcado: Forçar engine específico ("easyocr", "google", "claude")

        Returns:
            Dict com resultado do processamento + metadados de qual engine usou
        """
        resultado_final = None
        engine_usada = None

        # Se modo forçado, usar diretamente
        if modo_forcado:
            if modo_forcado == "easyocr":
                return self._processar_com_easyocr(imagem_bytes)
            elif modo_forcado == "google":
                return self._processar_com_google(imagem_bytes)
            elif modo_forcado == "claude":
                return self._processar_com_claude(imagem_bytes)

        # NIVEL 1: Tentar EasyOCR (sempre primeiro, gratis)
        print("[SCAN] Tentando EasyOCR (gratis)...")
        resultado_easy = self._processar_com_easyocr(imagem_bytes)

        if resultado_easy['sucesso']:
            confianca = resultado_easy.get('confianca', 0)
            produtos = resultado_easy.get('produtos', [])

            # Se resultado bom, retornar
            if confianca >= self.confianca_minima_easyocr and len(produtos) >= self.produtos_minimos:
                print(f"[OK] EasyOCR foi suficiente! Confiança: {confianca}%")
                resultado_easy['metadados']['decisao'] = {
                    'engine_escolhida': 'EasyOCR',
                    'motivo': 'Confiança suficiente',
                    'confianca': confianca,
                    'tentativas': ['easyocr']
                }
                return resultado_easy

            print(f"[AVISO]  EasyOCR com baixa confiança ({confianca}%) ou poucos produtos ({len(produtos)})")

        # Se usuário prefere só grátis e não tem créditos, retornar EasyOCR mesmo com baixa confiança
        if usuario_prefere_gratis and not usuario_tem_creditos_api:
            print("[INFO]  Retornando EasyOCR (usuário prefere grátis)")
            resultado_easy['metadados']['decisao'] = {
                'engine_escolhida': 'EasyOCR',
                'motivo': 'Usuário prefere gratuito',
                'confianca': resultado_easy.get('confianca', 0),
                'tentativas': ['easyocr']
            }
            return resultado_easy

        # NÍVEL 2: Tentar Google Vision (se disponível)
        if self._google_vision_disponivel():
            print("[SCAN] Tentando Google Vision...")
            resultado_google = self._processar_com_google(imagem_bytes)

            if resultado_google['sucesso']:
                produtos = resultado_google.get('produtos', [])

                if len(produtos) >= self.produtos_minimos:
                    print(f"[OK] Google Vision encontrou {len(produtos)} produtos!")
                    resultado_google['metadados']['decisao'] = {
                        'engine_escolhida': 'Google Vision',
                        'motivo': 'EasyOCR insuficiente, Google melhorou',
                        'tentativas': ['easyocr', 'google_vision']
                    }
                    return resultado_google

        # NÍVEL 3: Claude Vision (último recurso, mais caro mas mais preciso)
        if self._claude_vision_disponivel() and usuario_tem_creditos_api:
            print("[SCAN] Tentando Claude Vision (premium)...")
            resultado_claude = self._processar_com_claude(imagem_bytes)

            if resultado_claude['sucesso']:
                print(f"[OK] Claude Vision processou com sucesso!")
                resultado_claude['metadados']['decisao'] = {
                    'engine_escolhida': 'Claude Vision',
                    'motivo': 'Engines anteriores falharam, usando premium',
                    'tentativas': ['easyocr', 'google_vision', 'claude_vision']
                }
                return resultado_claude

        # Se chegou aqui, retornar melhor resultado que conseguimos
        print("[AVISO]  Retornando melhor resultado disponível (EasyOCR)")
        resultado_easy['metadados']['decisao'] = {
            'engine_escolhida': 'EasyOCR (fallback)',
            'motivo': 'Outros engines indisponíveis',
            'tentativas': ['easyocr']
        }
        return resultado_easy

    def _processar_com_easyocr(self, imagem_bytes: bytes) -> Dict:
        """Processa com EasyOCR ou Tesseract como fallback"""
        # Tentar EasyOCR primeiro
        try:
            from app.utils.easyocr_processor import get_easyocr_processor

            ocr = get_easyocr_processor()
            resultado = ocr.extrair_produtos_nota_fiscal(imagem_bytes)

            # Calcular confiança
            if resultado['sucesso'] and resultado.get('produtos'):
                confianca_produtos = ocr.calcular_confianca_produtos(resultado['produtos'])
                resultado['confianca'] = confianca_produtos
                resultado['metadados'] = resultado.get('metadados', {})
                resultado['metadados']['engine'] = 'EasyOCR'

            return resultado

        except ImportError:
            print("[AVISO]  EasyOCR não disponível, usando Tesseract...")
            return self._processar_com_tesseract(imagem_bytes)
        except Exception as e:
            print(f"[AVISO]  EasyOCR falhou ({e}), tentando Tesseract...")
            return self._processar_com_tesseract(imagem_bytes)

    def _processar_com_tesseract(self, imagem_bytes: bytes) -> Dict:
        """Processa com Tesseract OCR melhorado"""
        try:
            from app.utils.ocr_nota_fiscal import get_ocr_nota_fiscal

            ocr = get_ocr_nota_fiscal()
            resultado = ocr.processar_nota_fiscal(imagem_bytes)

            if resultado.get('sucesso'):
                # Adaptar formato para o sistema híbrido
                return {
                    'sucesso': True,
                    'produtos': resultado.get('produtos', []),
                    'total': resultado.get('total_nota'),
                    'supermercado': resultado.get('supermercado'),
                    'data_compra': resultado.get('data_compra'),
                    'confianca': resultado.get('confianca', 50),
                    'metadados': {
                        'engine': 'Tesseract',
                        'total_produtos': resultado.get('total_produtos', 0),
                        'verificado': resultado.get('verificado', False)
                    }
                }
            else:
                return {
                    'sucesso': False,
                    'erro': resultado.get('erro', 'Erro no processamento'),
                    'produtos': [],
                    'confianca': 0,
                    'metadados': {'engine': 'Tesseract'}
                }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Tesseract falhou: {str(e)}',
                'produtos': [],
                'confianca': 0,
                'metadados': {'engine': 'Tesseract'}
            }

    def _processar_com_google(self, imagem_bytes: bytes) -> Dict:
        """Processa com Google Vision (placeholder - implementar se necessário)"""
        # TODO: Implementar Google Vision
        return {
            'sucesso': False,
            'erro': 'Google Vision não configurado',
            'produtos': [],
            'confianca': 0
        }

    def _processar_com_claude(self, imagem_bytes: bytes) -> Dict:
        """Processa com Claude Vision"""
        try:
            from app.utils.claude_vision_ocr import get_claude_vision_ocr

            ocr = get_claude_vision_ocr()
            resultado = ocr.extrair_produtos_nota_fiscal(
                imagem_bytes=imagem_bytes,
                formato_imagem="image/jpeg"
            )

            if resultado.get('sucesso', True) and resultado.get('produtos'):
                produtos_validos = ocr.validar_e_corrigir_produtos(resultado['produtos'])
                resultado['produtos'] = [
                    {
                        'nome': p['nome'],
                        'preco': p['preco'],
                        'quantidade': p.get('quantidade', '1')
                    }
                    for p in produtos_validos
                ]
                resultado['confianca'] = 99.0  # Claude é muito preciso

            return resultado

        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Claude Vision falhou: {str(e)}',
                'produtos': [],
                'confianca': 0
            }

    def _google_vision_disponivel(self) -> bool:
        """Verifica se Google Vision está configurado"""
        # TODO: Verificar se credenciais Google estão disponíveis
        return False  # Por enquanto desabilitado

    def _claude_vision_disponivel(self) -> bool:
        """Verifica se Claude Vision está configurado"""
        return bool(os.getenv('ANTHROPIC_API_KEY'))


def get_ocr_hibrido() -> OCRHibrido:
    """Factory function"""
    return OCRHibrido()
