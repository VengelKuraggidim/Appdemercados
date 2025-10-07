from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CarteiraCreate(BaseModel):
    """Schema para criação de carteira"""
    usuario_nome: str = Field(..., min_length=3, max_length=50)
    cpf: Optional[str] = Field(None, min_length=11, max_length=14)
    senha: Optional[str] = Field(None, min_length=4)


class LoginRequest(BaseModel):
    """Schema para login"""
    cpf: str = Field(..., min_length=11, max_length=14)
    senha: str = Field(..., min_length=4)


class LoginResponse(BaseModel):
    """Schema de resposta do login"""
    sucesso: bool
    mensagem: str
    usuario_nome: Optional[str] = None
    saldo: Optional[float] = None
    token: Optional[str] = None  # JWT token para sessão


class CarteiraResponse(BaseModel):
    """Schema de resposta da carteira"""
    id: int
    usuario_nome: str
    saldo: float
    data_criacao: datetime
    ultima_atualizacao: datetime

    class Config:
        from_attributes = True


class TransacaoResponse(BaseModel):
    """Schema de resposta de transação"""
    id: int
    tipo: str
    quantidade: float
    descricao: Optional[str]
    data_transacao: datetime

    class Config:
        from_attributes = True


class SaldoResponse(BaseModel):
    """Resposta simplificada do saldo"""
    usuario_nome: str
    saldo: float
    total_minerado: float
    total_gasto: float
    ultima_atualizacao: datetime
    # Reputação
    reputacao: int = 100
    total_validacoes_feitas: int = 0
    total_validacoes_recebidas: int = 0
    validacoes_positivas: int = 0
    validacoes_negativas: int = 0
