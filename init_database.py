"""
Inicializa o banco de dados criando todas as tabelas
"""
from app.models.database import init_db

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_db()
    print("✓ Banco de dados inicializado com sucesso!")
