"""
Schemas Pydantic para Lista de Compras
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ItemListaCreate(BaseModel):
    """Schema para criar item na lista"""
    nome_produto: str = Field(..., min_length=2, max_length=200)
    quantidade: int = Field(default=1, ge=1, le=100)


class ItemListaUpdate(BaseModel):
    """Schema para atualizar item"""
    quantidade: Optional[int] = Field(None, ge=1, le=100)
    comprado: Optional[bool] = None


class ItemListaResponse(BaseModel):
    """Schema de resposta do item"""
    id: int
    nome_produto: str
    quantidade: int
    comprado: bool
    melhor_preco: Optional[float] = None
    melhor_supermercado: Optional[str] = None
    data_comparacao: Optional[datetime] = None

    class Config:
        from_attributes = True


class ListaComprasCreate(BaseModel):
    """Schema para criar lista de compras"""
    nome: str = Field(default="Minha Lista", max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ListaComprasUpdate(BaseModel):
    """Schema para atualizar lista"""
    nome: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ListaComprasResponse(BaseModel):
    """Schema de resposta da lista"""
    id: int
    nome: str
    usuario_nome: str
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    ativa: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    itens: List[ItemListaResponse] = []
    total_itens: int = 0
    itens_comprados: int = 0

    class Config:
        from_attributes = True


class SupermercadoComparacao(BaseModel):
    """Supermercado na comparacao"""
    nome: str
    total: float
    itens_disponiveis: int
    distancia_km: Optional[float] = None
    endereco: Optional[str] = None
    itens: List[dict] = []


class ComparacaoListaResponse(BaseModel):
    """Resultado da comparacao de lista"""
    lista_id: int
    nome_lista: str
    total_itens: int
    supermercados: List[SupermercadoComparacao]
    melhor_supermercado: Optional[SupermercadoComparacao] = None
    economia_potencial: float = 0.0
