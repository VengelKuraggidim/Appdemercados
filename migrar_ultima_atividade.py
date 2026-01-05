#!/usr/bin/env python3
"""
Script para migrar o banco de dados e adicionar coluna ultima_atividade
para controle de usuários inativos (status "soneca")
"""
from app.models.database import engine
from sqlalchemy import text


def migrar():
    with engine.connect() as conn:
        # Adicionar coluna ultima_atividade
        try:
            conn.execute(text("ALTER TABLE carteiras ADD COLUMN ultima_atividade TIMESTAMP"))
            print("[OK] Coluna 'ultima_atividade' adicionada")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("[INFO] Coluna 'ultima_atividade' ja existe")
            else:
                print(f"[ERRO] Erro ao adicionar 'ultima_atividade': {e}")

        # Preencher valores nulos com ultima_atualizacao (para usuarios existentes)
        try:
            conn.execute(text("""
                UPDATE carteiras
                SET ultima_atividade = ultima_atualizacao
                WHERE ultima_atividade IS NULL
            """))
            print("[OK] Valores de 'ultima_atividade' preenchidos com 'ultima_atualizacao'")
        except Exception as e:
            print(f"[WARN] Erro ao preencher valores: {e}")

        conn.commit()
        print("\n[OK] Migracao concluida!")


if __name__ == "__main__":
    migrar()
