from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func

from app.models.database import get_db, init_db, Produto, Preco, Alerta
from app.models.schemas import (
    BuscaRequest, ProdutoResponse, PrecoResponse,
    ComparacaoResponse, AlertaCreate, AlertaResponse
)
from app.models.schemas_manual import (
    PrecoManualCreate, ContribuicaoResponse, EstatisticasContribuicao
)
from app.scrapers.scraper_manager import ScraperManager
from app.utils.comparador import Comparador

app = FastAPI(
    title="Comparador de Preços",
    description="API para comparar preços de produtos em supermercados",
    version="1.0.0"
)

# CORS configuration for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize scrapers and comparador
scraper_manager = ScraperManager()
comparador = Comparador()


@app.get("/")
async def root():
    return {
        "message": "API Comparador de Preços",
        "version": "1.0.0",
        "endpoints": {
            "buscar": "/api/buscar",
            "comparar": "/api/comparar",
            "produtos": "/api/produtos",
            "alertas": "/api/alertas",
            "supermercados": "/api/supermercados"
        }
    }


@app.get("/api/supermercados")
async def listar_supermercados():
    """Lista todos os supermercados disponíveis"""
    return {
        "supermercados": scraper_manager.get_available_supermarkets(),
        "total": len(scraper_manager.get_available_supermarkets())
    }


@app.post("/api/buscar")
async def buscar_produtos(
    request: BuscaRequest,
    db: Session = Depends(get_db)
):
    """
    Busca produtos em todos os supermercados ou em supermercados específicos
    """
    if not request.termo or len(request.termo.strip()) < 2:
        raise HTTPException(status_code=400, detail="Termo de busca muito curto")

    # Search in supermarkets
    produtos_encontrados = scraper_manager.search_all(
        termo=request.termo,
        supermercados=request.supermercados
    )

    if not produtos_encontrados:
        return {
            "termo": request.termo,
            "total": 0,
            "produtos": [],
            "message": "Nenhum produto encontrado"
        }

    # Save to database
    produtos_salvos = []
    for item in produtos_encontrados:
        try:
            # Check if product exists
            produto = db.query(Produto).filter(
                Produto.nome.ilike(f"%{item['nome'][:50]}%")
            ).first()

            if not produto:
                produto = Produto(
                    nome=item['nome'],
                    marca=item.get('marca'),
                    categoria=None
                )
                db.add(produto)
                db.flush()

            # Add price
            preco = Preco(
                produto_id=produto.id,
                supermercado=item['supermercado'],
                preco=item['preco'],
                em_promocao=item.get('em_promocao', False),
                url=item['url'],
                disponivel=item.get('disponivel', True),
                data_coleta=datetime.now()
            )
            db.add(preco)
            produtos_salvos.append(item)

        except Exception as e:
            print(f"Error saving product: {e}")
            continue

    db.commit()

    return {
        "termo": request.termo,
        "total": len(produtos_salvos),
        "produtos": produtos_salvos
    }


@app.get("/api/comparar/{produto_nome}")
async def comparar_precos(
    produto_nome: str,
    db: Session = Depends(get_db)
):
    """
    Compara preços de um produto específico entre supermercados
    """
    # Get recent prices (last 24 hours)
    data_limite = datetime.now() - timedelta(hours=24)

    precos = db.query(Preco).join(Produto).filter(
        Produto.nome.ilike(f"%{produto_nome}%"),
        Preco.data_coleta >= data_limite,
        Preco.disponivel == True
    ).all()

    if not precos:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Use comparador to analyze prices
    resultado = comparador.comparar_precos(precos)

    return resultado


@app.get("/api/produtos", response_model=List[ProdutoResponse])
async def listar_produtos(
    skip: int = 0,
    limit: int = 50,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista produtos cadastrados"""
    query = db.query(Produto)

    if categoria:
        query = query.filter(Produto.categoria == categoria)

    produtos = query.offset(skip).limit(limit).all()
    return produtos


@app.get("/api/produtos/{produto_id}/historico")
async def historico_precos(
    produto_id: int,
    dias: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Obtém histórico de preços de um produto"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    data_limite = datetime.now() - timedelta(days=dias)

    precos = db.query(Preco).filter(
        Preco.produto_id == produto_id,
        Preco.data_coleta >= data_limite
    ).order_by(Preco.data_coleta.desc()).all()

    return {
        "produto": produto,
        "periodo_dias": dias,
        "total_registros": len(precos),
        "historico": precos
    }


@app.post("/api/alertas", response_model=AlertaResponse)
async def criar_alerta(
    alerta: AlertaCreate,
    db: Session = Depends(get_db)
):
    """Cria alerta de preço para um produto"""
    produto = db.query(Produto).filter(Produto.id == alerta.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    novo_alerta = Alerta(**alerta.dict())
    db.add(novo_alerta)
    db.commit()
    db.refresh(novo_alerta)

    return novo_alerta


@app.get("/api/alertas")
async def listar_alertas(
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista alertas cadastrados"""
    query = db.query(Alerta)

    if ativo is not None:
        query = query.filter(Alerta.ativo == ativo)

    alertas = query.all()
    return {"total": len(alertas), "alertas": alertas}


@app.delete("/api/alertas/{alerta_id}")
async def deletar_alerta(
    alerta_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um alerta"""
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    db.delete(alerta)
    db.commit()

    return {"message": "Alerta deletado com sucesso"}


@app.get("/api/melhores-ofertas")
async def melhores_ofertas(
    limite: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Lista as melhores ofertas disponíveis"""
    data_limite = datetime.now() - timedelta(hours=24)

    # Get products on sale
    precos = db.query(Preco).filter(
        Preco.em_promocao == True,
        Preco.data_coleta >= data_limite,
        Preco.disponivel == True
    ).order_by(Preco.preco.asc()).limit(limite).all()

    return {
        "total": len(precos),
        "ofertas": precos
    }


# ============================================
# ENDPOINTS DE CONTRIBUIÇÃO MANUAL
# ============================================

@app.post("/api/contribuir", response_model=ContribuicaoResponse)
async def adicionar_preco_manual(
    contribuicao: PrecoManualCreate,
    db: Session = Depends(get_db)
):
    """
    Permite que usuários contribuam adicionando preços manualmente
    """
    # Busca ou cria o produto
    produto = db.query(Produto).filter(
        Produto.nome.ilike(f"%{contribuicao.produto_nome}%")
    ).first()

    if not produto:
        produto = Produto(
            nome=contribuicao.produto_nome,
            marca=contribuicao.produto_marca,
            categoria=None  # Pode ser categorizado depois
        )
        db.add(produto)
        db.flush()

    # Adiciona o preço
    novo_preco = Preco(
        produto_id=produto.id,
        supermercado=contribuicao.supermercado,
        preco=contribuicao.preco,
        em_promocao=contribuicao.em_promocao,
        manual=True,
        usuario_nome=contribuicao.usuario_nome,
        localizacao=contribuicao.localizacao,
        observacao=contribuicao.observacao,
        foto_url=contribuicao.foto_url,
        disponivel=True,
        verificado=False,  # Requer verificação
        data_coleta=datetime.now()
    )

    db.add(novo_preco)
    db.commit()
    db.refresh(novo_preco)

    return ContribuicaoResponse(
        id=novo_preco.id,
        produto_nome=produto.nome,
        marca=produto.marca,
        supermercado=novo_preco.supermercado,
        preco=novo_preco.preco,
        em_promocao=novo_preco.em_promocao,
        localizacao=novo_preco.localizacao,
        data_cadastro=novo_preco.data_coleta,
        usuario_nome=novo_preco.usuario_nome,
        verificado=novo_preco.verificado
    )


@app.get("/api/contribuicoes", response_model=List[ContribuicaoResponse])
async def listar_contribuicoes(
    skip: int = 0,
    limit: int = 50,
    apenas_verificadas: bool = False,
    db: Session = Depends(get_db)
):
    """Lista contribuições dos usuários"""
    query = db.query(Preco).filter(Preco.manual == True)

    if apenas_verificadas:
        query = query.filter(Preco.verificado == True)

    precos = query.order_by(Preco.data_coleta.desc()).offset(skip).limit(limit).all()

    return [
        ContribuicaoResponse(
            id=p.id,
            produto_nome=p.produto.nome,
            marca=p.produto.marca,
            supermercado=p.supermercado,
            preco=p.preco,
            em_promocao=p.em_promocao,
            localizacao=p.localizacao,
            data_cadastro=p.data_coleta,
            usuario_nome=p.usuario_nome,
            verificado=p.verificado
        )
        for p in precos
    ]


@app.get("/api/estatisticas-contribuicoes", response_model=EstatisticasContribuicao)
async def estatisticas_contribuicoes(db: Session = Depends(get_db)):
    """Estatísticas sobre contribuições dos usuários"""

    total_contribuicoes = db.query(Preco).filter(Preco.manual == True).count()

    produtos_unicos = db.query(func.count(func.distinct(Preco.produto_id))).filter(
        Preco.manual == True
    ).scalar()

    supermercados_unicos = db.query(func.count(func.distinct(Preco.supermercado))).filter(
        Preco.manual == True
    ).scalar()

    hoje = datetime.now().date()
    contribuicoes_hoje = db.query(Preco).filter(
        Preco.manual == True,
        func.date(Preco.data_coleta) == hoje
    ).count()

    ultima = db.query(Preco).filter(Preco.manual == True).order_by(
        Preco.data_coleta.desc()
    ).first()

    return EstatisticasContribuicao(
        total_contribuicoes=total_contribuicoes,
        total_produtos=produtos_unicos or 0,
        total_supermercados=supermercados_unicos or 0,
        contribuicoes_hoje=contribuicoes_hoje,
        ultima_contribuicao=ultima.data_coleta if ultima else None
    )


@app.get("/api/supermercados-contribuidos")
async def listar_supermercados_contribuidos(db: Session = Depends(get_db)):
    """Lista supermercados que já receberam contribuições"""
    supermercados = db.query(Preco.supermercado, func.count(Preco.id)).filter(
        Preco.manual == True
    ).group_by(Preco.supermercado).all()

    return {
        "supermercados": [
            {"nome": s[0], "total_precos": s[1]}
            for s in supermercados
        ]
    }


@app.post("/api/extrair-preco-foto")
async def extrair_preco_de_foto(file: UploadFile = File(...)):
    """
    Extrai preço e informações do produto de uma foto usando OCR
    """
    try:
        from app.utils.ocr import get_ocr_instance

        # Ler arquivo
        contents = await file.read()

        # Validar tipo de arquivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

        # Validar tamanho (max 10MB)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagem muito grande (max 10MB)")

        # Processar com OCR
        ocr = get_ocr_instance()
        resultado = ocr.extrair_de_imagem(contents)

        if 'erro' in resultado:
            return {
                "sucesso": False,
                "erro": resultado['erro'],
                "sugestao": "Tente tirar outra foto mais nítida do preço"
            }

        # Verificar se encontrou preço
        if not resultado.get('preco'):
            return {
                "sucesso": False,
                "erro": "Não foi possível identificar o preço na imagem",
                "texto_extraido": resultado.get('texto_completo', ''),
                "sugestao": "Certifique-se de que o preço está visível e nítido"
            }

        return {
            "sucesso": True,
            "preco": resultado.get('preco'),
            "produto_nome": resultado.get('produto_nome'),
            "marca": resultado.get('marca'),
            "precos_encontrados": resultado.get('precos_encontrados', []),
            "texto_extraido": resultado.get('texto_completo', ''),
            "confianca": resultado.get('confianca', 0.0),
            "mensagem": "Preço extraído com sucesso! Verifique e confirme os dados."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")


@app.post("/api/contribuir-com-foto")
async def contribuir_com_foto(
    file: UploadFile = File(...),
    supermercado: str = None,
    localizacao: str = None,
    observacao: str = None,
    usuario_nome: str = None,
    db: Session = Depends(get_db)
):
    """
    Contribuir direto com foto - extrai dados e salva automaticamente
    """
    try:
        from app.utils.ocr import get_ocr_instance
        import base64

        # Extrair dados da foto
        contents = await file.read()
        ocr = get_ocr_instance()
        resultado = ocr.extrair_de_imagem(contents)

        if 'erro' in resultado or not resultado.get('preco'):
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair preço da imagem. Use o formulário manual."
            )

        # Salvar foto (base64 simplificado para demo)
        foto_base64 = base64.b64encode(contents[:5000]).decode('utf-8')  # Primeiros 5KB
        foto_url = f"data:image/jpeg;base64,{foto_base64[:100]}..."  # Truncado

        # Criar produto se não existir
        produto_nome = resultado.get('produto_nome', 'Produto da Foto')
        produto = db.query(Produto).filter(
            Produto.nome.ilike(f"%{produto_nome}%")
        ).first()

        if not produto:
            produto = Produto(
                nome=produto_nome,
                marca=resultado.get('marca'),
                categoria=None
            )
            db.add(produto)
            db.flush()

        # Adicionar preço
        novo_preco = Preco(
            produto_id=produto.id,
            supermercado=supermercado or "Não informado",
            preco=resultado['preco'],
            em_promocao=False,
            manual=True,
            usuario_nome=usuario_nome,
            localizacao=localizacao,
            observacao=f"Extraído via OCR. {observacao or ''}",
            foto_url=foto_url,
            disponivel=True,
            verificado=False,
            data_coleta=datetime.now()
        )

        db.add(novo_preco)
        db.commit()
        db.refresh(novo_preco)

        return {
            "sucesso": True,
            "mensagem": "Contribuição adicionada com sucesso!",
            "contribuicao": ContribuicaoResponse(
                id=novo_preco.id,
                produto_nome=produto.nome,
                marca=produto.marca,
                supermercado=novo_preco.supermercado,
                preco=novo_preco.preco,
                em_promocao=novo_preco.em_promocao,
                localizacao=novo_preco.localizacao,
                data_cadastro=novo_preco.data_coleta,
                usuario_nome=novo_preco.usuario_nome,
                verificado=novo_preco.verificado
            ),
            "dados_extraidos": {
                "preco": resultado['preco'],
                "produto": resultado.get('produto_nome'),
                "marca": resultado.get('marca'),
                "texto": resultado.get('texto_completo', '')[:200]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
