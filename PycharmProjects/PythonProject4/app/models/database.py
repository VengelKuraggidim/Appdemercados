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
