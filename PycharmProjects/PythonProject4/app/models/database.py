from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()


class SupermercadoEnum(str, enum.Enum):
    CARREFOUR = "carrefour"
    PAO_ACUCAR = "pao_acucar"
    EXTRA = "extra"
    MERCADO_LIVRE = "mercado_livre"
    ATACADAO = "atacadao"


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    marca = Column(String)
    categoria = Column(String, index=True)
    descricao = Column(String)
    data_criacao = Column(DateTime, default=datetime.now)

    precos = relationship("Preco", back_populates="produto")
    alertas = relationship("Alerta", back_populates="produto")


class Preco(Base):
    __tablename__ = "precos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    supermercado = Column(String, nullable=False)  # Changed to String for flexibility
    preco = Column(Float, nullable=False)
    preco_original = Column(Float)
    em_promocao = Column(Boolean, default=False)
    url = Column(String, default="")
    disponivel = Column(Boolean, default=True)
    data_coleta = Column(DateTime, default=datetime.now, index=True)

    # Manual entry fields
    manual = Column(Boolean, default=False)  # Is this a manual entry?
    usuario_nome = Column(String)  # Who added it
    localizacao = Column(String)  # Store location
    observacao = Column(String)  # Additional notes
    foto_url = Column(String)  # Photo proof
    verificado = Column(Boolean, default=False)  # Admin verified?

    # Geolocation fields
    latitude = Column(Float, index=True)  # Store latitude
    longitude = Column(Float, index=True)  # Store longitude
    endereco = Column(String)  # Full address

    produto = relationship("Produto", back_populates="precos")


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    preco_alvo = Column(Float, nullable=False)
    email = Column(String)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.now)
    data_ultima_notificacao = Column(DateTime)

    produto = relationship("Produto", back_populates="alertas")


class Carteira(Base):
    """Carteira de criptomoeda do usuário"""
    __tablename__ = "carteiras"

    id = Column(Integer, primary_key=True, index=True)
    usuario_nome = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True)  # CPF do usuário
    senha_hash = Column(String)  # Senha criptografada
    saldo = Column(Float, default=0.0)  # Saldo em tokens
    data_criacao = Column(DateTime, default=datetime.now)
    ultima_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    transacoes = relationship("Transacao", back_populates="carteira")


class Transacao(Base):
    """Histórico de transações de tokens"""
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    carteira_id = Column(Integer, ForeignKey("carteiras.id"), nullable=False)
    tipo = Column(String, nullable=False)  # "mineracao", "busca", "bonus"
    quantidade = Column(Float, nullable=False)  # Positivo = ganho, Negativo = gasto
    descricao = Column(String)
    data_transacao = Column(DateTime, default=datetime.now, index=True)

    # Referências opcionais
    preco_id = Column(Integer, ForeignKey("precos.id"))  # Se foi por contribuição

    carteira = relationship("Carteira", back_populates="transacoes")


# Database connection
DATABASE_URL = "sqlite:///./precos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
