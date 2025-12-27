"""
Script de migração para adicionar novas colunas na tabela sugestoes
"""
import sqlite3

DATABASE_PATH = "app_mercados.db"

def migrar():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Lista de colunas para adicionar
    novas_colunas = [
        ("tokens_escrow", "REAL DEFAULT 0.0"),
        ("moderador_implementador", "VARCHAR"),
        ("data_candidatura_moderador", "DATETIME"),
        ("data_implementacao", "DATETIME"),
        ("motivo_cancelamento", "VARCHAR"),
    ]

    # Verificar quais colunas já existem
    cursor.execute("PRAGMA table_info(sugestoes)")
    colunas_existentes = [row[1] for row in cursor.fetchall()]

    # Adicionar colunas que não existem
    for nome_coluna, tipo_coluna in novas_colunas:
        if nome_coluna not in colunas_existentes:
            try:
                sql = f"ALTER TABLE sugestoes ADD COLUMN {nome_coluna} {tipo_coluna}"
                print(f"Adicionando coluna: {nome_coluna}")
                cursor.execute(sql)
                conn.commit()
                print(f"✓ Coluna {nome_coluna} adicionada com sucesso")
            except Exception as e:
                print(f"✗ Erro ao adicionar coluna {nome_coluna}: {e}")
        else:
            print(f"○ Coluna {nome_coluna} já existe")

    conn.close()
    print("\n✓ Migração concluída!")

if __name__ == "__main__":
    migrar()
