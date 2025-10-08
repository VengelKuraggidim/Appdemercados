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

    # Sistema de Reputação
    reputacao = Column(Integer, default=100)  # Começa com 100 pontos
    total_validacoes_feitas = Column(Integer, default=0)  # Quantas validações fez
    total_validacoes_recebidas = Column(Integer, default=0)  # Quantas validações recebeu
    validacoes_positivas = Column(Integer, default=0)  # Validações positivas que recebeu
    validacoes_negativas = Column(Integer, default=0)  # Validações negativas que recebeu

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


class Comentario(Base):
    """Comentários gerais da comunidade"""
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_nome = Column(String, nullable=False, index=True)
    conteudo = Column(String, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now, index=True)
    editado = Column(Boolean, default=False)
    data_edicao = Column(DateTime)

    # Relacionamento com votos
    votos = relationship("VotoComentario", back_populates="comentario")


class VotoComentario(Base):
    """Votos (like/dislike) em comentários"""
    __tablename__ = "votos_comentarios"

    id = Column(Integer, primary_key=True, index=True)
    comentario_id = Column(Integer, ForeignKey("comentarios.id"), nullable=False)
    usuario_nome = Column(String, nullable=False, index=True)
    tipo = Column(String, nullable=False)  # "like" ou "dislike"
    data_voto = Column(DateTime, default=datetime.now)

    # Relacionamento
    comentario = relationship("Comentario", back_populates="votos")


class StatusSugestao(str, enum.Enum):
    """Status possíveis de uma sugestão"""
    PENDENTE_APROVACAO = "pendente_aprovacao"  # Aguardando aprovação do admin
    EM_VOTACAO = "em_votacao"  # Aprovada e em votação
    APROVADA = "aprovada"  # Atingiu 60% dos votos
    REJEITADA = "rejeitada"  # Não atingiu votos suficientes
    IMPLEMENTADA = "implementada"  # Já foi implementada
    CANCELADA = "cancelada"  # Cancelada pelo admin


class Sugestao(Base):
    """Sugestões da comunidade para melhorias"""
    __tablename__ = "sugestoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_nome = Column(String, nullable=False, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    status = Column(SQLEnum(StatusSugestao), default=StatusSugestao.PENDENTE_APROVACAO, index=True)

    # Votação
    total_votos_favor = Column(Integer, default=0)  # Soma dos votos a favor
    total_votos_contra = Column(Integer, default=0)  # Soma dos votos contra
    total_tokens_votados = Column(Integer, default=0)  # Total de tokens usados na votação
    porcentagem_aprovacao = Column(Float, default=0.0)  # % de aprovação

    # Aprovação inicial
    aprovadores = Column(String)  # Lista de usuários que aprovaram (separados por vírgula)
    total_aprovadores = Column(Integer, default=0)

    # Datas
    data_criacao = Column(DateTime, default=datetime.now, index=True)
    data_aprovacao = Column(DateTime)  # Quando foi aprovada para votação
    data_finalizacao = Column(DateTime)  # Quando foi finalizada (aprovada/rejeitada)

    # Observações
    motivo_rejeicao = Column(String)  # Se foi rejeitada, por quê

    votos = relationship("Voto", back_populates="sugestao", cascade="all, delete-orphan")


class Voto(Base):
    """Votos em sugestões (votação quadrática)"""
    __tablename__ = "votos"

    id = Column(Integer, primary_key=True, index=True)
    sugestao_id = Column(Integer, ForeignKey("sugestoes.id"), nullable=False, index=True)
    usuario_nome = Column(String, nullable=False, index=True)

    # Votação quadrática: quanto mais tokens usar, mais caro fica cada voto
    tokens_usados = Column(Integer, nullable=False)  # Quantos tokens gastou
    votos_gerados = Column(Integer, nullable=False)  # Quantos votos isso gerou (sqrt dos tokens)
    voto_favor = Column(Boolean, nullable=False)  # True = a favor, False = contra

    data_voto = Column(DateTime, default=datetime.now, index=True)

    sugestao = relationship("Sugestao", back_populates="votos")


class ValidacaoPreco(Base):
    """Validações de preços entre usuários (sistema de reputação)"""
    __tablename__ = "validacoes_precos"

    id = Column(Integer, primary_key=True, index=True)
    preco_id = Column(Integer, ForeignKey("precos.id"), nullable=False, index=True)
    validador_nome = Column(String, nullable=False, index=True)  # Quem validou
    validado_nome = Column(String, nullable=False, index=True)  # Quem foi validado

    # Validação
    aprovado = Column(Boolean, nullable=False)  # True = correto, False = incorreto
    motivo = Column(String)  # Motivo da rejeição (se aprovado = False)

    # Dados da validação
    preco_sugerido = Column(Float)  # Se rejeitou, qual seria o preço correto?
    diferenca_percentual = Column(Float)  # % de diferença entre preços

    data_validacao = Column(DateTime, default=datetime.now, index=True)


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
