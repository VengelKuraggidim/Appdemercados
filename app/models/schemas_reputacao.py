"""
Schemas Pydantic para o sistema de reputação
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ValidarPrecoRequest(BaseModel):
    """Schema para validar um preço"""
    preco_id: int
    validador_nome: str
    aprovado: bool  # True = preço correto, False = preço incorreto
    motivo: Optional[str] = None  # Se reprovado, qual o motivo?
    preco_sugerido: Optional[float] = None  # Se reprovado, qual seria o preço correto?


class ValidacaoResponse(BaseModel):
    """Schema para resposta de validação"""
    id: int
    preco_id: int
    validador_nome: str
    validado_nome: str
    aprovado: bool
    motivo: Optional[str]
    preco_sugerido: Optional[float]
    diferenca_percentual: Optional[float]
    data_validacao: datetime

    class Config:
        from_attributes = True


class ReputacaoResponse(BaseModel):
    """Schema para resposta de reputação do usuário"""
    usuario_nome: str
    reputacao: float
    total_validacoes_feitas: int
    total_validacoes_recebidas: int
    validacoes_positivas: int
    validacoes_negativas: int
    taxa_aprovacao: float  # % de validações positivas
    nivel_confianca: str  # "Muito Alto", "Alto", "Médio", "Baixo"


class ContribuicaoParaValidar(BaseModel):
    """Schema para contribuição que precisa ser validada"""
    preco_id: int
    produto_nome: str
    produto_marca: Optional[str]
    preco: float
    supermercado: str
    usuario_nome: str
    usuario_reputacao: float
    localizacao: Optional[str]
    data_coleta: datetime
    total_validacoes: int  # Quantas validações já recebeu
    aprovacoes: int  # Quantas aprovações
    rejeicoes: int  # Quantas rejeições
    precisa_validacao: bool  # Se ainda precisa de mais validações

    class Config:
        from_attributes = True
