#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar colunas CPF e senha
"""
from app.models.database import engine
from sqlalchemy import text

def migrar():
    with engine.connect() as conn:
        try:
            # Adicionar coluna CPF
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN cpf TEXT"))
            print("✅ Coluna 'cpf' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'cpf' já existe")
            else:
                print(f"❌ Erro ao adicionar 'cpf': {e}")

        try:
            # Adicionar coluna senha_hash
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN senha_hash TEXT"))
            print("✅ Coluna 'senha_hash' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'senha_hash' já existe")
            else:
                print(f"❌ Erro ao adicionar 'senha_hash': {e}")

        conn.commit()
        print("\n✅ Migração concluída!")

if __name__ == "__main__":
    migrar()
