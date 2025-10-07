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

        # Adicionar colunas de reputação
        try:
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN reputacao INTEGER DEFAULT 100"))
            print("✅ Coluna 'reputacao' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'reputacao' já existe")
            else:
                print(f"❌ Erro ao adicionar 'reputacao': {e}")

        try:
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN total_validacoes_feitas INTEGER DEFAULT 0"))
            print("✅ Coluna 'total_validacoes_feitas' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'total_validacoes_feitas' já existe")
            else:
                print(f"❌ Erro ao adicionar 'total_validacoes_feitas': {e}")

        try:
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN total_validacoes_recebidas INTEGER DEFAULT 0"))
            print("✅ Coluna 'total_validacoes_recebidas' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'total_validacoes_recebidas' já existe")
            else:
                print(f"❌ Erro ao adicionar 'total_validacoes_recebidas': {e}")

        try:
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN validacoes_positivas INTEGER DEFAULT 0"))
            print("✅ Coluna 'validacoes_positivas' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'validacoes_positivas' já existe")
            else:
                print(f"❌ Erro ao adicionar 'validacoes_positivas': {e}")

        try:
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN validacoes_negativas INTEGER DEFAULT 0"))
            print("✅ Coluna 'validacoes_negativas' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  Coluna 'validacoes_negativas' já existe")
            else:
                print(f"❌ Erro ao adicionar 'validacoes_negativas': {e}")

        # Criar tabela validacoes_precos se não existir
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS validacoes_precos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preco_id INTEGER NOT NULL,
                    validador_nome TEXT NOT NULL,
                    validado_nome TEXT NOT NULL,
                    aprovado BOOLEAN NOT NULL,
                    motivo TEXT,
                    preco_sugerido REAL,
                    diferenca_percentual REAL,
                    data_validacao TIMESTAMP NOT NULL,
                    FOREIGN KEY(preco_id) REFERENCES precos(id)
                )
            """))
            print("✅ Tabela 'validacoes_precos' criada")
        except Exception as e:
            print(f"ℹ️  Tabela 'validacoes_precos': {e}")

        conn.commit()
        print("\n✅ Migração concluída!")

if __name__ == "__main__":
    migrar()
