from app.models.database import SessionLocal, Produto
import re

db = SessionLocal()

# Buscar produto batata
produto = db.query(Produto).filter(Produto.nome.ilike('%batata%')).first()

if produto:
    print(f'Nome antigo: {produto.nome}')

    # Limpar nome
    nome_limpo = produto.nome
    # Remover aspas e números do final
    nome_limpo = re.sub(r'\s*["\'\—]\s*\d*$', '', nome_limpo)
    # Remover aspas restantes
    nome_limpo = nome_limpo.replace('"', '').replace("'", '')
    nome_limpo = nome_limpo.strip()

    produto.nome = nome_limpo
    db.commit()

    print(f'Nome novo: {produto.nome}')
    print('✓ Nome atualizado!')
else:
    print('Produto não encontrado')

db.close()
