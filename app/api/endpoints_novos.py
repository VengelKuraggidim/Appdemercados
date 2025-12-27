"""
Novos endpoints para Lista de Compras, Codigo de Barras e Validacao Automatica
Este arquivo sera integrado ao main.py
"""

# IMPORTS NECESSARIOS (adicionar ao inicio do main.py):
# from app.models.database import ListaCompras, ItemLista, ValidacaoAutomatica
# from app.models.schemas_lista import ListaComprasCreate, ItemListaCreate
# from app.utils.auto_moderador import get_auto_moderador
# from app.utils.ean_service import ean_service
# from app.utils.comparador_lista import get_comparador_lista


# ============================================
# ENDPOINTS DE LISTA DE COMPRAS
# ============================================

# @app.post("/api/listas")
async def criar_lista(lista, usuario_nome, db):
    """Criar nova lista de compras"""
    from app.models.database import ListaCompras

    nova_lista = ListaCompras(
        usuario_nome=usuario_nome,
        nome=lista.nome,
        latitude=lista.latitude,
        longitude=lista.longitude
    )
    db.add(nova_lista)
    db.commit()
    db.refresh(nova_lista)

    return {
        "id": nova_lista.id,
        "nome": nova_lista.nome,
        "usuario_nome": nova_lista.usuario_nome,
        "data_criacao": nova_lista.data_criacao,
        "sucesso": True
    }


# @app.get("/api/listas/usuario/{usuario_nome}")
async def listar_listas_usuario(usuario_nome, db):
    """Lista todas as listas de compras do usuario"""
    from app.models.database import ListaCompras

    listas = db.query(ListaCompras).filter(
        ListaCompras.usuario_nome == usuario_nome,
        ListaCompras.ativa == True
    ).order_by(ListaCompras.data_atualizacao.desc()).all()

    return {
        "listas": [{
            "id": l.id,
            "nome": l.nome,
            "total_itens": len(l.itens),
            "itens_comprados": len([i for i in l.itens if i.comprado]),
            "data_criacao": l.data_criacao
        } for l in listas],
        "total": len(listas)
    }


# @app.post("/api/listas/{lista_id}/comparar")
async def comparar_lista(lista_id, latitude, longitude, db):
    """Comparar precos da lista entre supermercados"""
    from app.models.database import ListaCompras
    from app.utils.comparador_lista import get_comparador_lista

    lista = db.query(ListaCompras).filter(ListaCompras.id == lista_id).first()
    if not lista:
        return {"erro": "Lista nao encontrada"}

    comparador = get_comparador_lista(db)
    resultado = comparador.comparar_lista(
        itens=lista.itens,
        latitude=latitude or lista.latitude,
        longitude=longitude or lista.longitude
    )

    return {
        "lista_id": lista_id,
        "nome_lista": lista.nome,
        "total_itens": len(lista.itens),
        **resultado
    }


# @app.post("/api/buscar-ean")
async def buscar_por_ean(ean, db):
    """Buscar produto por codigo de barras EAN"""
    from app.models.database import Produto, Preco
    from app.utils.ean_service import ean_service

    ean = ean.strip()

    # Primeiro verifica no banco local
    produto = db.query(Produto).filter(Produto.ean == ean).first()

    if produto:
        precos = db.query(Preco).filter(
            Preco.produto_id == produto.id,
            Preco.disponivel == True
        ).order_by(Preco.data_coleta.desc()).limit(10).all()

        return {
            "sucesso": True,
            "fonte": "banco_local",
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "marca": produto.marca,
                "ean": produto.ean
            },
            "precos": [{
                "supermercado": p.supermercado,
                "preco": p.preco
            } for p in precos]
        }

    # Busca em APIs externas
    resultado = ean_service.buscar_por_ean(ean)

    if not resultado:
        return {
            "sucesso": False,
            "erro": "Produto nao encontrado",
            "ean": ean
        }

    # Cria produto no banco
    novo_produto = Produto(
        nome=resultado['nome'],
        marca=resultado.get('marca'),
        categoria=resultado.get('categoria'),
        ean=ean
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return {
        "sucesso": True,
        "fonte": resultado['fonte'],
        "produto": {
            "id": novo_produto.id,
            "nome": novo_produto.nome,
            "ean": ean,
            "imagem_url": resultado.get('imagem_url')
        },
        "precos": []
    }
