from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class PrecoManualCreate(BaseModel):
    """Schema for manually adding a price"""
    produto_nome: str = Field(..., min_length=3, max_length=200, description="Nome do produto")
    produto_marca: Optional[str] = Field(None, max_length=100, description="Marca do produto")
    supermercado: str = Field(..., description="Nome do supermercado/loja")
    preco: float = Field(..., gt=0, description="Preço do produto")
    em_promocao: bool = Field(default=False, description="Produto está em promoção?")
    localizacao: Optional[str] = Field(None, description="Cidade/bairro do supermercado")
    observacao: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    foto_url: Optional[str] = Field(None, description="URL da foto do preço (comprovante)")
    usuario_nome: Optional[str] = Field(None, max_length=100, description="Nome de quem cadastrou")
    latitude: Optional[float] = Field(None, description="Latitude da localização")
    longitude: Optional[float] = Field(None, description="Longitude da localização")

    @validator('preco')
    def validar_preco(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        if v > 1000000:
            raise ValueError('Preço muito alto, verifique')
        return round(v, 2)

    @validator('supermercado')
    def validar_supermercado(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Nome do supermercado muito curto')
        return v.strip().lower()


class ContribuicaoResponse(BaseModel):
    """Response for a user contribution"""
    id: int
    produto_nome: str
    marca: Optional[str]
    supermercado: str
    preco: float
    em_promocao: bool
    localizacao: Optional[str]
    data_cadastro: datetime
    usuario_nome: Optional[str]
    verificado: bool = False

    class Config:
        from_attributes = True


class EstatisticasContribuicao(BaseModel):
    """Statistics about user contributions"""
    total_contribuicoes: int
    total_produtos: int
    total_supermercados: int
    contribuicoes_hoje: int
    ultima_contribuicao: Optional[datetime]
