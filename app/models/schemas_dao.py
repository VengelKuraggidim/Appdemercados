"""
Schemas Pydantic para o sistema DAO (Comentários e Sugestões)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# COMENTÁRIOS
# ============================================

class ComentarioCreate(BaseModel):
    """Schema para criar comentário"""
    usuario_nome: str
    conteudo: str = Field(..., min_length=1, max_length=1000)


class ComentarioResponse(BaseModel):
    """Schema para resposta de comentário"""
    id: int
    usuario_nome: str
    conteudo: str
    data_criacao: datetime
    editado: bool
    data_edicao: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SUGESTÕES
# ============================================

class StatusSugestaoEnum(str, Enum):
    """Status possíveis de uma sugestão"""
    PENDENTE_APROVACAO = "pendente_aprovacao"
    EM_VOTACAO = "em_votacao"
    APROVADA = "aprovada"
    EM_IMPLEMENTACAO = "em_implementacao"
    IMPLEMENTADA = "implementada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"


class SugestaoCreate(BaseModel):
    """Schema para criar sugestão"""
    usuario_nome: str
    titulo: str = Field(..., min_length=5, max_length=200)
    descricao: str = Field(..., min_length=10, max_length=2000)


class SugestaoResponse(BaseModel):
    """Schema para resposta de sugestão"""
    id: int
    usuario_nome: str
    titulo: str
    descricao: str
    status: str
    total_votos_favor: int
    total_votos_contra: int
    total_tokens_votados: int
    porcentagem_aprovacao: float
    total_aprovadores: int
    aprovadores: Optional[str] = None  # Lista de moderadores que aprovaram (separados por vírgula)
    # Escrow de tokens
    tokens_escrow: float = 0.0
    moderador_implementador: Optional[str] = None
    data_candidatura_moderador: Optional[datetime] = None
    # Datas
    data_criacao: datetime
    data_aprovacao: Optional[datetime] = None
    data_finalizacao: Optional[datetime] = None
    data_implementacao: Optional[datetime] = None
    motivo_rejeicao: Optional[str] = None
    motivo_cancelamento: Optional[str] = None

    class Config:
        from_attributes = True


class SugestaoDetalhadaResponse(SugestaoResponse):
    """Schema detalhado com lista de votantes"""
    aprovadores_lista: List[str] = []
    total_usuarios_votaram: int = 0


# ============================================
# VOTAÇÃO
# ============================================

class VotoCreate(BaseModel):
    """Schema para criar voto"""
    sugestao_id: int
    usuario_nome: str
    tokens_usados: int = Field(..., ge=1, le=100, description="Mínimo 1, máximo 100 tokens por voto")
    voto_favor: bool  # True = a favor, False = contra


class VotoResponse(BaseModel):
    """Schema para resposta de voto"""
    id: int
    sugestao_id: int
    usuario_nome: str
    tokens_usados: int
    votos_gerados: int
    voto_favor: bool
    data_voto: datetime

    class Config:
        from_attributes = True


class ResultadoVotacao(BaseModel):
    """Schema para resultado de votação"""
    sucesso: bool
    mensagem: str
    tokens_gastos: int
    votos_gerados: int
    saldo_restante: int
    sugestao: SugestaoResponse


# ============================================
# APROVAÇÃO DE SUGESTÕES
# ============================================

class AprovarSugestaoRequest(BaseModel):
    """Schema para aprovar sugestão para votação"""
    sugestao_id: int
    usuario_nome: str  # Usuário que está aprovando


class RejeitarSugestaoRequest(BaseModel):
    """Schema para rejeitar sugestão"""
    sugestao_id: int
    usuario_admin: str = "Vengel"  # Admin que rejeitou
    motivo: str = Field(..., min_length=10, max_length=500)


# ============================================
# ESTATÍSTICAS
# ============================================

class EstatisticasDAO(BaseModel):
    """Estatísticas do sistema DAO"""
    total_comentarios: int
    total_sugestoes: int
    sugestoes_pendentes: int
    sugestoes_em_votacao: int
    sugestoes_aprovadas: int
    sugestoes_implementadas: int
    total_usuarios_participantes: int
    total_tokens_votados: int


# ============================================
# MODERADORES (CONTRATO INTELIGENTE)
# ============================================

class ModeradorCreate(BaseModel):
    """Schema para criar moderador"""
    usuario_nome: str


class ModeradorResponse(BaseModel):
    """Schema para resposta de moderador"""
    id: int
    usuario_nome: str
    ativo: bool
    total_sugestoes_aprovadas: int
    total_sugestoes_implementadas: int
    total_sugestoes_canceladas: int
    tokens_ganhos_total: float
    reputacao_moderador: int
    data_cadastro: datetime
    ultima_atividade: datetime

    class Config:
        from_attributes = True


class AceitarImplementarRequest(BaseModel):
    """Schema para moderador aceitar implementar uma sugestão"""
    sugestao_id: int
    moderador_nome: str


class MarcarImplementadaRequest(BaseModel):
    """Schema para marcar sugestão como implementada"""
    sugestao_id: int
    moderador_nome: str
    observacao: Optional[str] = None


class CancelarImplementacaoRequest(BaseModel):
    """Schema para cancelar implementação"""
    sugestao_id: int
    moderador_nome: str
    motivo: str = Field(..., min_length=10, max_length=500)
    devolver_tokens: bool = True  # Se True, devolve tokens ao criador
