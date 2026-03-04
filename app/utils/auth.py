import os
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models.database import get_db, Carteira, Moderador

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "appdemercados-dev-secret-key-2024")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 72

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def criar_token(usuario_nome: str, cpf: str) -> str:
    """Cria um JWT token para o usuario"""
    payload = {
        "sub": usuario_nome,
        "cpf": cpf,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Decodifica e valida um JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado. Faca login novamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido.")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Carteira:
    """Dependency que retorna o usuario autenticado via JWT"""
    payload = decodificar_token(credentials.credentials)
    usuario_nome = payload.get("sub")
    if not usuario_nome:
        raise HTTPException(status_code=401, detail="Token invalido.")

    carteira = db.query(Carteira).filter(Carteira.usuario_nome == usuario_nome).first()
    if not carteira:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado.")

    return carteira


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_optional),
    db: Session = Depends(get_db),
) -> Carteira | None:
    """Dependency que retorna o usuario se autenticado, ou None"""
    if credentials is None:
        return None
    try:
        payload = decodificar_token(credentials.credentials)
    except HTTPException:
        return None

    usuario_nome = payload.get("sub")
    if not usuario_nome:
        return None

    return db.query(Carteira).filter(Carteira.usuario_nome == usuario_nome).first()


async def get_moderador(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Carteira:
    """Dependency que valida que o usuario e um moderador ativo"""
    payload = decodificar_token(credentials.credentials)
    usuario_nome = payload.get("sub")
    if not usuario_nome:
        raise HTTPException(status_code=401, detail="Token invalido.")

    carteira = db.query(Carteira).filter(Carteira.usuario_nome == usuario_nome).first()
    if not carteira:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado.")

    moderador = db.query(Moderador).filter(
        Moderador.usuario_nome == usuario_nome,
        Moderador.ativo == True,
    ).first()
    if not moderador:
        raise HTTPException(status_code=403, detail="Voce nao e um moderador autorizado.")

    return carteira
