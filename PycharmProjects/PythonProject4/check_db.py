"""
Verifica a estrutura da tabela sugestoes
"""
import sqlite3

DATABASE_PATH = "app_mercados.db"

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Ver estrutura da tabela sugestoes
cursor.execute("PRAGMA table_info(sugestoes)")
colunas = cursor.fetchall()

print("Colunas na tabela sugestoes:")
print("=" * 60)
for col in colunas:
    print(f"{col[0]:3} | {col[1]:30} | {col[2]:15}")

conn.close()
