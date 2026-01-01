"""
Sistema de Auto-Moderacao de Precos
Aprova/rejeita contribuicoes automaticamente com base na comparacao de precos
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Optional
import statistics

from app.models.database import Preco, Produto, Carteira


class AutoModerador:
    """
    Sistema de moderacao automatica de precos.
    Aprova/rejeita precos baseado em comparacao com dados existentes.
    Nao ha envolvimento de usuarios na moderacao.
    """

    # Limites de validacao
    LIMITE_APROVACAO_AUTOMATICA = 30.0  # +/- 30% da mediana = aprovado
    LIMITE_REJEICAO_AUTOMATICA = 50.0   # > 50% diferenca = rejeitado
    MINIMO_PRECOS_COMPARACAO = 2        # Precisa de pelo menos 2 precos para comparar
    DIAS_COMPARACAO = 30                # Compara com precos dos ultimos 30 dias

    # Alteracoes de reputacao
    REPUTACAO_APROVADO = 3
    REPUTACAO_APROVADO_AVISO = 1
    REPUTACAO_REJEITADO = -5

    def __init__(self, db: Session):
        self.db = db

    def validar_preco(self, preco_id: int) -> Dict:
        """
        Valida uma contribuicao de preco automaticamente.

        Returns:
            {
                'aprovado': bool,
                'motivo': str,
                'tipo': str,
                'diferenca_percentual': float,
                'mediana': float,
                'reputacao_alteracao': int
            }
        """
        # Busca o preco submetido
        preco = self.db.query(Preco).filter(Preco.id == preco_id).first()
        if not preco:
            return {'erro': 'Preco nao encontrado', 'aprovado': False}

        if not preco.manual:
            return {'erro': 'Apenas precos manuais sao validados', 'aprovado': True}

        # Busca precos existentes para comparacao
        data_limite = datetime.now() - timedelta(days=self.DIAS_COMPARACAO)

        precos_existentes = self.db.query(Preco).filter(
            Preco.produto_id == preco.produto_id,
            Preco.id != preco_id,
            Preco.data_coleta >= data_limite,
            Preco.disponivel == True,
            Preco.preco > 0
        ).all()

        # Sem dados suficientes para comparar - aprova automaticamente
        if len(precos_existentes) < self.MINIMO_PRECOS_COMPARACAO:
            resultado = self._aprovar_sem_comparacao(preco)
            self._registrar_validacao(preco, resultado, 0)
            return resultado

        # Calcula mediana dos precos
        valores = [p.preco for p in precos_existentes]
        mediana = statistics.median(valores)

        # Calcula diferenca percentual
        if mediana > 0:
            diferenca = abs((preco.preco - mediana) / mediana) * 100
        else:
            diferenca = 0

        # Determina resultado
        if diferenca <= self.LIMITE_APROVACAO_AUTOMATICA:
            resultado = self._aprovar_preco(preco, mediana, diferenca)
        elif diferenca > self.LIMITE_REJEICAO_AUTOMATICA:
            resultado = self._rejeitar_preco(preco, mediana, diferenca)
        else:
            # Entre 30-50%: aprova com aviso
            resultado = self._aprovar_com_aviso(preco, mediana, diferenca)

        # Registra validacao
        self._registrar_validacao(preco, resultado, len(precos_existentes))

        # Atualiza reputacao do usuario
        self._atualizar_reputacao(preco.usuario_nome, resultado['reputacao_alteracao'])

        # Atualiza status de verificacao do preco
        preco.verificado = resultado['aprovado']
        self.db.commit()

        return resultado

    def _aprovar_preco(self, preco: Preco, mediana: float, diferenca: float) -> Dict:
        """Aprova preco dentro do limite aceitavel"""
        return {
            'aprovado': True,
            'motivo': f'Preco validado automaticamente. Diferenca de {diferenca:.1f}% da mediana (R$ {mediana:.2f})',
            'diferenca_percentual': diferenca,
            'mediana': mediana,
            'reputacao_alteracao': self.REPUTACAO_APROVADO,
            'tipo': 'aprovado'
        }

    def _aprovar_com_aviso(self, preco: Preco, mediana: float, diferenca: float) -> Dict:
        """Aprova com aviso (30-50% de diferenca)"""
        return {
            'aprovado': True,
            'motivo': f'Preco aceito com aviso. Diferenca de {diferenca:.1f}% da mediana (R$ {mediana:.2f})',
            'diferenca_percentual': diferenca,
            'mediana': mediana,
            'reputacao_alteracao': self.REPUTACAO_APROVADO_AVISO,
            'tipo': 'aprovado_com_aviso'
        }

    def _rejeitar_preco(self, preco: Preco, mediana: float, diferenca: float) -> Dict:
        """Rejeita preco fora do limite aceitavel"""
        return {
            'aprovado': False,
            'motivo': f'Preco rejeitado automaticamente. Diferenca de {diferenca:.1f}% e muito alta em relacao a mediana (R$ {mediana:.2f})',
            'diferenca_percentual': diferenca,
            'mediana': mediana,
            'reputacao_alteracao': self.REPUTACAO_REJEITADO,
            'tipo': 'rejeitado'
        }

    def _aprovar_sem_comparacao(self, preco: Preco) -> Dict:
        """Aprova quando nao ha dados suficientes para comparar"""
        return {
            'aprovado': True,
            'motivo': 'Preco aceito - poucos dados para comparacao (primeiro registro)',
            'diferenca_percentual': 0,
            'mediana': preco.preco,
            'reputacao_alteracao': self.REPUTACAO_APROVADO,
            'tipo': 'aprovado_primeiro'
        }

    def _registrar_validacao(self, preco: Preco, resultado: Dict, total_comparados: int):
        """Registra a decisao de validacao no banco"""
        # Importa aqui para evitar import circular
        try:
            from app.models.database import ValidacaoAutomatica

            validacao = ValidacaoAutomatica(
                preco_id=preco.id,
                usuario_nome=preco.usuario_nome or 'anonimo',
                aprovado=resultado['aprovado'],
                motivo=resultado['motivo'],
                tipo=resultado.get('tipo'),
                preco_submetido=preco.preco,
                mediana_existente=resultado.get('mediana'),
                diferenca_percentual=resultado.get('diferenca_percentual'),
                total_precos_comparados=total_comparados,
                limite_aprovacao=self.LIMITE_APROVACAO_AUTOMATICA,
                limite_rejeicao=self.LIMITE_REJEICAO_AUTOMATICA,
                reputacao_alteracao=resultado.get('reputacao_alteracao', 0)
            )
            self.db.add(validacao)
        except ImportError:
            # Modelo ainda nao existe, ignora
            pass

    def _atualizar_reputacao(self, usuario_nome: str, alteracao: int):
        """Atualiza reputacao do usuario baseado no resultado da validacao"""
        if not usuario_nome:
            return

        carteira = self.db.query(Carteira).filter(
            Carteira.usuario_nome == usuario_nome
        ).first()

        if carteira:
            nova_reputacao = (carteira.reputacao or 100) + alteracao
            carteira.reputacao = max(0, min(200, nova_reputacao))


def get_auto_moderador(db: Session) -> AutoModerador:
    """Factory para criar instancia do AutoModerador"""
    return AutoModerador(db)
