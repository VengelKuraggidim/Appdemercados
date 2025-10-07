from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Supermercado(str, Enum):
    CARREFOUR = "carrefour"
    PAO_ACUCAR = "pao_acucar"
    EXTRA = "extra"
    MERCADO_LIVRE = "mercado_livre"
    ATACADAO = "atacadao"


class ProdutoBase(BaseModel):
    nome: str
    marca: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None


class PrecoBase(BaseModel):
    produto_id: int
    supermercado: Supermercado
    preco: float
    preco_original: Optional[float] = None
    em_promocao: bool = False
    url: str
    disponivel: bool = True
    data_coleta: datetime = Field(default_factory=datetime.now)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoResponse(ProdutoBase):
    id: int
    data_criacao: datetime

    class Config:
        from_attributes = True


class PrecoResponse(PrecoBase):
    id: int
    produto: ProdutoResponse

    class Config:
        from_attributes = True


class ComparacaoResponse(BaseModel):
    produto: str
    precos: List[PrecoResponse]
    melhor_preco: PrecoResponse
    diferenca_percentual: float


class AlertaCreate(BaseModel):
    produto_id: int
    preco_alvo: float
    email: Optional[str] = None
    ativo: bool = True


class AlertaResponse(AlertaCreate):
    id: int
    data_criacao: datetime

    class Config:
        from_attributes = True


class BuscaRequest(BaseModel):
    termo: str
    supermercados: Optional[List[Supermercado]] = None
