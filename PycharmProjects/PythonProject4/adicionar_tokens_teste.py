#!/usr/bin/env python3
"""
Script para adicionar tokens de teste à carteira Vengel
"""

from app.models.database import SessionLocal
from app.utils.crypto_manager import CryptoManager

def adicionar_tokens_teste():
    db = SessionLocal()
    try:
        crypto = CryptoManager(db)

        # Adicionar 1000 tokens para testes
        resultado = crypto.minerar_tokens(
            usuario_nome="Vengel",
            quantidade=1000,
            descricao="Tokens para testes de votação DAO"
        )

        if resultado['sucesso']:
            print(f"✅ {resultado['mensagem']}")
            print(f"💰 Saldo atual: {resultado['saldo_atual']} tokens")
        else:
            print(f"❌ Erro: {resultado['mensagem']}")

    except Exception as e:
        print(f"❌ Erro ao adicionar tokens: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    adicionar_tokens_teste()
