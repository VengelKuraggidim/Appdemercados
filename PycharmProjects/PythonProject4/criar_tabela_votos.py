"""
Script para criar a tabela VotoComentario no banco de dados
"""

from app.models.database import Base, engine

if __name__ == "__main__":
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("A tabela votos_comentarios foi adicionada ao banco.")
