#!/usr/bin/env python3
"""
Script para criar tabela de votos em comentários
"""
from app.models.database import engine
from sqlalchemy import text

def migrar():
    with engine.connect() as conn:
        try:
            # Criar tabela de votos em comentários
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS votos_comentarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comentario_id INTEGER NOT NULL,
                    usuario_nome TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    data_voto TIMESTAMP NOT NULL,
                    FOREIGN KEY(comentario_id) REFERENCES comentarios(id),
                    UNIQUE(comentario_id, usuario_nome)
                )
            """))
            print("✅ Tabela 'votos_comentarios' criada")

            # Criar índices
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_votos_comentarios_comentario
                ON votos_comentarios(comentario_id)
            """))
            print("✅ Índice criado para comentario_id")

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_votos_comentarios_usuario
                ON votos_comentarios(usuario_nome)
            """))
            print("✅ Índice criado para usuario_nome")

        except Exception as e:
            print(f"❌ Erro: {e}")

        conn.commit()
        print("\n✅ Migração concluída!")

if __name__ == "__main__":
    migrar()
