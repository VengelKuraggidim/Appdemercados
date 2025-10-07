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
    REJEITADA = "rejeitada"
    IMPLEMENTADA = "implementada"
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
    data_criacao: datetime
    data_aprovacao: Optional[datetime] = None
    data_finalizacao: Optional[datetime] = None
    motivo_rejeicao: Optional[str] = None

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
