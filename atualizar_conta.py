#!/usr/bin/env python3
"""
Script para atualizar conta existente com CPF e senha
"""
from app.models.database import SessionLocal, Carteira
from app.utils.crypto_manager import CryptoManager

def atualizar_conta():
    db = SessionLocal()
    crypto = CryptoManager(db)

    # Buscar conta Vengel
    carteira = db.query(Carteira).filter(Carteira.usuario_nome == "Vengel").first()

    if carteira:
        # Atualizar com CPF e senha temporária
        cpf = input("Digite seu CPF (apenas números): ")
        senha = input("Digite sua senha: ")

        carteira.cpf = cpf
        carteira.senha_hash = crypto._hash_senha(senha)

        db.commit()
        print(f"\n✅ Conta atualizada!")
        print(f"Usuário: {carteira.usuario_nome}")
        print(f"CPF: {cpf}")
        print(f"Saldo: {carteira.saldo} tokens")
    else:
        print("❌ Conta 'Vengel' não encontrada")

    db.close()

if __name__ == "__main__":
    atualizar_conta()
