from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
import os

from app.models.database import get_db, init_db, Produto, Preco, Alerta, Carteira, Transacao, Comentario, Sugestao, Voto, StatusSugestao, ValidacaoPreco
from app.models.schemas import (
    BuscaRequest, ProdutoResponse, PrecoResponse,
    ComparacaoResponse, AlertaCreate, AlertaResponse
)
from app.models.schemas_manual import (
    PrecoManualCreate, ContribuicaoResponse, EstatisticasContribuicao
)
from app.models.schemas_crypto import (
    CarteiraCreate, CarteiraResponse, TransacaoResponse, SaldoResponse,
    LoginRequest, LoginResponse
)
from app.models.schemas_dao import (
    ComentarioCreate, ComentarioResponse,
    SugestaoCreate, SugestaoResponse, SugestaoDetalhadaResponse,
    VotoCreate, VotoResponse, ResultadoVotacao,
    AprovarSugestaoRequest, RejeitarSugestaoRequest,
    EstatisticasDAO
)
from app.models.schemas_reputacao import (
    ValidarPrecoRequest, ValidacaoResponse, ReputacaoResponse,
    ContribuicaoParaValidar
)
from app.scrapers.scraper_manager import ScraperManager
from app.utils.comparador import Comparador
from app.utils.geolocalizacao import (
    GeoLocalizacao, AnalisadorCustoBeneficio, ranquear_precos_por_custo_beneficio
)
from app.utils.crypto_manager import CryptoManager

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


@app.get("/api")
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
    usuario_nome: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Busca produtos em todos os supermercados ou em supermercados específicos
    Prioriza busca no banco de dados de contribuições
    CUSTO: 1 token por busca (se usuário informado)
    """
    if not request.termo or len(request.termo.strip()) < 2:
        raise HTTPException(status_code=400, detail="Termo de busca muito curto")

    # Sistema de tokens: cobrar pela busca
    crypto = CryptoManager(db)
    custo_info = None

    if usuario_nome:
        resultado_gasto = crypto.gastar_tokens(usuario_nome, descricao=f"Busca por '{request.termo}'")
        if not resultado_gasto["sucesso"]:
            raise HTTPException(
                status_code=402,  # Payment Required
                detail={
                    "erro": "Saldo insuficiente",
                    "mensagem": resultado_gasto["mensagem"],
                    "saldo_atual": resultado_gasto["saldo_atual"],
                    "faltam": resultado_gasto["faltam"],
                    "dica": "Adicione preços para ganhar tokens!"
                }
            )
        custo_info = {
            "tokens_gastos": resultado_gasto["tokens_gastos"],
            "saldo_restante": resultado_gasto["saldo_atual"]
        }

    # First, search in database (contributions)
    data_limite = datetime.now() - timedelta(days=30)  # Last 30 days

    precos_db = db.query(Preco).join(Produto).filter(
        Produto.nome.ilike(f"%{request.termo}%"),
        Preco.data_coleta >= data_limite,
        Preco.disponivel == True
    ).all()

    produtos_encontrados = []

    # Add products from database
    for preco in precos_db:
        produtos_encontrados.append({
            'nome': preco.produto.nome,
            'marca': preco.produto.marca,
            'preco': preco.preco,
            'em_promocao': preco.em_promocao,
            'url': preco.url or '#',
            'supermercado': preco.supermercado,
            'disponivel': preco.disponivel,
            'fonte': 'contribuicao' if preco.manual else 'scraper',
            'data_coleta': preco.data_coleta.isoformat() if preco.data_coleta else None
        })

    # If no results from DB, try scraping (may not work due to Google blocking)
    if not produtos_encontrados:
        try:
            produtos_scraped = scraper_manager.search_all(
                termo=request.termo,
                supermercados=request.supermercados
            )

            # Save scraped products to database
            for item in produtos_scraped:
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
                    produtos_encontrados.append(item)

                except Exception as e:
                    print(f"Error saving product: {e}")
                    continue

            db.commit()
        except Exception as e:
            print(f"Scraping error: {e}")

    resposta = {
        "termo": request.termo,
        "total": len(produtos_encontrados),
        "produtos": produtos_encontrados
    }

    if not produtos_encontrados:
        resposta["message"] = "Nenhum produto encontrado. Contribua adicionando preços!"

    # Adicionar informação de tokens se usuário fez a busca
    if custo_info:
        resposta["tokens"] = custo_info

    return resposta


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

@app.post("/api/contribuir")
async def adicionar_preco_manual(
    contribuicao: PrecoManualCreate,
    endereco: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Permite que usuários contribuam adicionando preços manualmente
    RECOMPENSA: 10 tokens por contribuição!
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
        data_coleta=datetime.now(),
        latitude=contribuicao.latitude,
        longitude=contribuicao.longitude,
        endereco=endereco
    )

    db.add(novo_preco)
    db.commit()
    db.refresh(novo_preco)

    # Sistema de tokens: recompensar pela contribuição
    crypto = CryptoManager(db)
    recompensa = crypto.minerar_tokens(
        usuario_nome=contribuicao.usuario_nome,
        preco_id=novo_preco.id
    )

    # Validação automática de preço (compara com outros preços)
    from app.utils.crypto_manager import ReputacaoManager
    rep_manager = ReputacaoManager(db)
    validacao_resultado = rep_manager.validar_preco_automaticamente(novo_preco.id)

    return {
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
        "recompensa": recompensa,
        "validacao": validacao_resultado
    }


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
    latitude: float = None,
    longitude: float = None,
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
            data_coleta=datetime.now(),
            latitude=latitude,
            longitude=longitude
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


# ============================================
# ENDPOINTS DE NOTA FISCAL (OCR)
# ============================================

@app.post("/api/escanear-nota-fiscal")
async def escanear_nota_fiscal(
    file: Optional[UploadFile] = File(None),
    usuario_nome: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    endereco: Optional[str] = Form(None),
    dados_manuais: Optional[str] = Form(None),  # JSON string via FormData
    db: Session = Depends(get_db)
):
    """
    Escaneia nota fiscal completa e extrai todos os produtos e preços
    RECOMPENSA: 10 tokens por produto extraído!

    Pode receber:
    - file: Imagem da nota (modo automático)
    - dados_manuais: JSON com dados já corrigidos (modo debug)
    """
    try:
        from app.utils.crypto_manager import CryptoManager
        import json

        print(f"DEBUG - Recebido: file={file}, usuario_nome={usuario_nome}, dados_manuais={dados_manuais}")

        # Modo 1: Dados manuais corrigidos (do debug OCR)
        if dados_manuais:
            resultado = json.loads(dados_manuais)
        # Modo 2: Upload de arquivo (automático)
        elif file:
            from app.utils.ocr_nota_fiscal import get_ocr_nota_fiscal

            # Validar arquivo
            contents = await file.read()

            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

            if len(contents) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Imagem muito grande (max 10MB)")

            # Processar nota fiscal
            ocr = get_ocr_nota_fiscal()
            resultado = ocr.processar_nota_fiscal(contents)
            print(f"DEBUG - Resultado OCR: sucesso={resultado.get('sucesso')}, produtos={len(resultado.get('produtos', []))}")
        else:
            raise HTTPException(status_code=400, detail="Envie um arquivo ou dados manuais")

        # Garantir que temos usuário
        if not usuario_nome:
            raise HTTPException(status_code=400, detail="usuario_nome é obrigatório")

        if not resultado['sucesso']:
            return {
                "sucesso": False,
                "erro": resultado.get('erro'),
                "sugestao": resultado.get('sugestao'),
                "texto_extraido": resultado.get('texto_extraido', '')[:500]
            }

        # Validar data da nota (últimos 30 dias)
        # TEMPORARIAMENTE DESABILITADO PARA TESTES
        # if resultado.get('data_compra'):
        #     try:
        #         data_nota = datetime.strptime(resultado['data_compra'], '%Y-%m-%dT%H:%M:%S')
        #         dias_atras = (datetime.now() - data_nota).days
        #
        #         if dias_atras > 30:
        #             return {
        #                 "sucesso": False,
        #                 "erro": "Nota fiscal muito antiga",
        #                 "sugestao": f"Esta nota é de {data_nota.strftime('%d/%m/%Y')} ({dias_atras} dias atrás). Por favor, envie apenas notas dos últimos 30 dias para manter os preços atualizados.",
        #                 "dias_atras": dias_atras
        #             }
        #     except:
        #         pass  # Se não conseguiu parsear, continua

        # Salvar produtos no banco
        produtos_salvos = []
        total_tokens_ganhos = 0

        for item in resultado['produtos']:
            # Buscar ou criar produto
            produto = db.query(Produto).filter(
                Produto.nome.ilike(f"%{item['nome'][:50]}%")
            ).first()

            if not produto:
                produto = Produto(
                    nome=item['nome'],
                    marca=None,
                    categoria=None
                )
                db.add(produto)
                db.flush()

            # Verificar se já existe preço similar (evitar duplicatas)
            from sqlalchemy import func, and_
            hoje = datetime.now().date()

            preco_existente = db.query(Preco).filter(
                and_(
                    Preco.produto_id == produto.id,
                    Preco.supermercado == resultado['supermercado'],
                    Preco.preco == item['preco'],
                    func.date(Preco.data_coleta) == hoje,
                    Preco.usuario_nome == usuario_nome
                )
            ).first()

            if preco_existente:
                # Já foi adicionado hoje, pular
                produtos_salvos.append({
                    'id': preco_existente.id,
                    'nome': item['nome'],
                    'preco': item['preco'],
                    'quantidade': item.get('quantidade', 1),
                    'duplicado': True
                })
                continue

            # Adicionar preço
            novo_preco = Preco(
                produto_id=produto.id,
                supermercado=resultado['supermercado'],
                preco=item['preco'],
                em_promocao=False,
                manual=True,
                usuario_nome=usuario_nome,
                localizacao=endereco,
                observacao=f"Extraído de nota fiscal. Qtd: {item.get('quantidade', 1)}. Data nota: {resultado.get('data_compra', 'N/A')}",
                disponivel=True,
                verificado=resultado.get('verificado', False),
                data_coleta=datetime.now(),  # Sempre usar data atual para busca funcionar
                latitude=latitude,
                longitude=longitude,
                endereco=endereco
            )

            db.add(novo_preco)
            db.flush()

            produtos_salvos.append({
                'id': novo_preco.id,
                'nome': produto.nome,
                'preco': item['preco'],
                'quantidade': item.get('quantidade', 1)
            })

            # Recompensar com tokens
            if usuario_nome:
                crypto = CryptoManager(db)
                recompensa = crypto.minerar_tokens(
                    usuario_nome=usuario_nome,
                    preco_id=novo_preco.id
                )
                total_tokens_ganhos += recompensa['tokens_ganhos']

        db.commit()

        return {
            "sucesso": True,
            "mensagem": f"✅ {len(produtos_salvos)} produtos extraídos da nota fiscal!",
            "supermercado": resultado['supermercado'],
            "data_compra": resultado.get('data_compra'),
            "total_produtos": len(produtos_salvos),
            "produtos_salvos": produtos_salvos,
            "total_nota": resultado.get('total_nota'),
            "soma_produtos": resultado.get('soma_produtos'),
            "verificado": resultado.get('verificado', False),
            "confianca": resultado.get('confianca', 0),
            "tokens_ganhos": total_tokens_ganhos if usuario_nome else 0,
            "texto_extraido": resultado.get('texto_completo', '')[:300]
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar nota fiscal: {str(e)}")


@app.post("/api/preview-nota-fiscal")
async def preview_nota_fiscal(file: UploadFile = File(...)):
    """
    Pré-visualização: extrai dados da nota fiscal sem salvar no banco
    Útil para o usuário revisar antes de confirmar
    """
    try:
        from app.utils.ocr_nota_fiscal import get_ocr_nota_fiscal

        contents = await file.read()

        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

        ocr = get_ocr_nota_fiscal()
        resultado = ocr.processar_nota_fiscal(contents)

        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@app.post("/api/debug-ocr")
async def debug_ocr(file: UploadFile = File(...)):
    """
    Debug: mostra o texto bruto extraído da imagem
    Útil para ajustar padrões regex
    """
    try:
        from app.utils.ocr_nota_fiscal import get_ocr_nota_fiscal

        contents = await file.read()

        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

        ocr = get_ocr_nota_fiscal()

        # Extrair texto
        print("DEBUG - Iniciando extração de texto...")
        texto = ocr.extrair_texto(contents)
        print(f"DEBUG - Texto extraído: {len(texto)} caracteres")
        print(f"DEBUG - Primeiras 500 caracteres: {texto[:500]}")

        # Tentar identificar supermercado e data
        supermercado = ocr.identificar_supermercado(texto)
        data_compra = ocr.extrair_data(texto)
        produtos = ocr.extrair_produtos(texto)
        total = ocr.extrair_total(texto)

        linhas = texto.split('\n')

        return {
            "sucesso": True,
            "texto_completo": texto,
            "total_caracteres": len(texto),
            "total_linhas": len(linhas),
            "supermercado_identificado": supermercado,
            "data_identificada": data_compra.isoformat() if data_compra else None,
            "produtos_encontrados": len(produtos),
            "produtos": produtos,  # Todos os produtos
            "total_encontrado": total,
            "todas_linhas": linhas,  # Todas as linhas
            "primeiras_30_linhas": linhas[:30],
            "debug_info": {
                "arquivo_nome": file.filename,
                "tipo_conteudo": file.content_type,
                "tamanho_bytes": len(contents),
                "texto_vazio": len(texto.strip()) == 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# ENDPOINTS DE GEOLOCALIZAÇÃO E CUSTO-BENEFÍCIO
# ============================================

@app.post("/api/buscar-otimizado")
async def buscar_produtos_otimizado(
    termo: str,
    latitude: float,
    longitude: float,
    tipo_transporte: str = "carro",
    considerar_tempo: bool = True,
    supermercados: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Busca produtos considerando geolocalização e custo-benefício
    Retorna produtos ordenados por melhor custo real (preço + deslocamento)
    Inclui produtos SEM GPS também, mas sem cálculo de distância
    """
    if not termo or len(termo.strip()) < 2:
        raise HTTPException(status_code=400, detail="Termo de busca muito curto")

    # Buscar TODOS os produtos (com ou sem GPS)
    data_limite = datetime.now() - timedelta(days=30)

    query = db.query(Preco).join(Produto).filter(
        Produto.nome.ilike(f"%{termo}%"),
        Preco.data_coleta >= data_limite,
        Preco.disponivel == True
    )

    if supermercados:
        query = query.filter(Preco.supermercado.in_(supermercados))

    precos = query.all()

    if not precos:
        return {
            "termo": termo,
            "total": 0,
            "produtos": [],
            "message": "Nenhum produto encontrado"
        }

    # Separar produtos com e sem GPS
    precos_com_gps = []
    precos_sem_gps = []

    for preco in precos:
        produto_info = {
            "id": preco.id,
            "nome": preco.produto.nome,
            "marca": preco.produto.marca,
            "preco": preco.preco,
            "supermercado": preco.supermercado,
            "em_promocao": preco.em_promocao,
            "endereco": preco.endereco,
            "localizacao": preco.localizacao,
            "data_coleta": preco.data_coleta.isoformat() if preco.data_coleta else None,
            "url": preco.url or '#',
            "disponivel": preco.disponivel,
            "fonte": 'contribuicao' if preco.manual else 'scraper'
        }

        if preco.latitude and preco.longitude:
            produto_info["latitude"] = preco.latitude
            produto_info["longitude"] = preco.longitude
            precos_com_gps.append(produto_info)
        else:
            precos_sem_gps.append(produto_info)

    # Ranquear produtos com GPS por custo-benefício
    resultados_com_gps = []
    if precos_com_gps:
        resultados_com_gps = ranquear_precos_por_custo_beneficio(
            precos_com_gps,
            latitude,
            longitude,
            tipo_transporte,
            considerar_tempo
        )

    # Ordenar produtos sem GPS apenas por preço
    precos_sem_gps.sort(key=lambda x: x['preco'])

    # Combinar: produtos com GPS (otimizados) + produtos sem GPS (por preço)
    resultados_finais = resultados_com_gps + precos_sem_gps

    return {
        "termo": termo,
        "total": len(resultados_finais),
        "com_gps": len(resultados_com_gps),
        "sem_gps": len(precos_sem_gps),
        "usuario": {
            "latitude": latitude,
            "longitude": longitude,
            "tipo_transporte": tipo_transporte
        },
        "produtos": resultados_finais,
        "aviso": f"Mostrando {len(resultados_com_gps)} produtos com análise de distância e {len(precos_sem_gps)} produtos apenas por preço" if precos_sem_gps else None
    }


@app.get("/api/analisar-economia")
async def analisar_economia_deslocamento(
    produto_id: int,
    latitude_usuario: float,
    longitude_usuario: float,
    tipo_transporte: str = "carro",
    considerar_tempo: bool = True,
    db: Session = Depends(get_db)
):
    """
    Analisa se vale a pena ir ao supermercado mais barato
    comparando com o mais próximo
    """
    # Buscar preços do produto com geolocalização
    data_limite = datetime.now() - timedelta(days=7)

    precos = db.query(Preco).filter(
        Preco.produto_id == produto_id,
        Preco.data_coleta >= data_limite,
        Preco.disponivel == True,
        Preco.latitude.isnot(None),
        Preco.longitude.isnot(None)
    ).all()

    if not precos or len(precos) < 2:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado ou insuficientes opções com localização"
        )

    geo = GeoLocalizacao()
    analisador = AnalisadorCustoBeneficio(tipo_transporte, considerar_tempo)

    # Calcular distâncias
    opcoes = []
    for preco in precos:
        distancia = geo.calcular_distancia(
            latitude_usuario,
            longitude_usuario,
            preco.latitude,
            preco.longitude
        )
        opcoes.append({
            "preco_obj": preco,
            "preco": preco.preco,
            "distancia": distancia,
            "supermercado": preco.supermercado,
            "endereco": preco.endereco
        })

    # Encontrar mais próximo e mais barato
    mais_proximo = min(opcoes, key=lambda x: x["distancia"])
    mais_barato = min(opcoes, key=lambda x: x["preco"])

    # Se são o mesmo, retornar informação simplificada
    if mais_proximo["preco_obj"].id == mais_barato["preco_obj"].id:
        return {
            "melhor_opcao": "unica",
            "mensagem": "O supermercado mais próximo já tem o melhor preço!",
            "detalhes": {
                "supermercado": mais_proximo["supermercado"],
                "preco": mais_proximo["preco"],
                "distancia_km": round(mais_proximo["distancia"], 2),
                "endereco": mais_proximo["endereco"]
            }
        }

    # Analisar economia
    analise = analisador.analisar_economia(
        preco_mais_proximo=mais_proximo["preco"],
        preco_mais_barato=mais_barato["preco"],
        distancia_mais_proximo_km=mais_proximo["distancia"],
        distancia_mais_barato_km=mais_barato["distancia"]
    )

    # Adicionar informações dos supermercados
    analise["local_proximo"]["supermercado"] = mais_proximo["supermercado"]
    analise["local_proximo"]["endereco"] = mais_proximo["endereco"]
    analise["local_barato"]["supermercado"] = mais_barato["supermercado"]
    analise["local_barato"]["endereco"] = mais_barato["endereco"]

    return {
        "produto": precos[0].produto.nome,
        "analise": analise,
        "todas_opcoes": [
            {
                "supermercado": o["supermercado"],
                "preco": o["preco"],
                "distancia_km": round(o["distancia"], 2),
                "endereco": o["endereco"]
            }
            for o in sorted(opcoes, key=lambda x: x["distancia"])
        ]
    }


@app.get("/api/calcular-distancia")
async def calcular_distancia(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
):
    """Calcula distância entre dois pontos em km"""
    geo = GeoLocalizacao()
    distancia = geo.calcular_distancia(lat1, lon1, lat2, lon2)

    return {
        "distancia_km": round(distancia, 2),
        "distancia_metros": round(distancia * 1000, 0)
    }


# ============================================
# ENDPOINTS DE CRIPTOMOEDA / CARTEIRA
# ============================================

@app.post("/api/carteira/criar", response_model=CarteiraResponse)
async def criar_carteira(
    carteira_data: CarteiraCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova carteira para o usuário
    Bônus inicial: 5 tokens
    """
    crypto = CryptoManager(db)
    carteira = crypto.criar_ou_obter_carteira(
        usuario_nome=carteira_data.usuario_nome,
        cpf=carteira_data.cpf,
        senha=carteira_data.senha
    )
    db.commit()
    db.refresh(carteira)

    return carteira


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Faz login com CPF e senha
    """
    crypto = CryptoManager(db)
    resultado = crypto.autenticar(login_data.cpf, login_data.senha)

    return LoginResponse(**resultado)


@app.post("/api/auth/registrar", response_model=LoginResponse)
async def registrar(
    usuario_nome: str,
    cpf: str,
    senha: str,
    db: Session = Depends(get_db)
):
    """
    Registra novo usuário com CPF e senha
    """
    # Verificar se CPF já existe
    carteira_existente = db.query(Carteira).filter(Carteira.cpf == cpf).first()
    if carteira_existente:
        return LoginResponse(
            sucesso=False,
            mensagem="CPF já cadastrado"
        )

    crypto = CryptoManager(db)
    carteira = crypto.criar_ou_obter_carteira(
        usuario_nome=usuario_nome,
        cpf=cpf,
        senha=senha
    )
    db.commit()

    return LoginResponse(
        sucesso=True,
        mensagem="Cadastro realizado com sucesso!",
        usuario_nome=carteira.usuario_nome,
        saldo=carteira.saldo
    )


@app.get("/api/carteira/{usuario_nome}", response_model=SaldoResponse)
async def obter_carteira(
    usuario_nome: str,
    db: Session = Depends(get_db)
):
    """Obtém informações da carteira do usuário"""
    crypto = CryptoManager(db)
    saldo_info = crypto.obter_saldo(usuario_nome)

    return saldo_info


@app.get("/api/carteira/{usuario_nome}/historico", response_model=List[TransacaoResponse])
async def obter_historico_transacoes(
    usuario_nome: str,
    limite: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Obtém histórico de transações do usuário"""
    crypto = CryptoManager(db)
    transacoes = crypto.obter_historico(usuario_nome, limite)

    return transacoes


@app.get("/api/carteira/{usuario_nome}/pode-buscar")
async def verificar_saldo_para_busca(
    usuario_nome: str,
    db: Session = Depends(get_db)
):
    """Verifica se usuário tem saldo suficiente para fazer uma busca"""
    crypto = CryptoManager(db)
    pode_buscar = crypto.verificar_saldo_suficiente(usuario_nome)

    saldo_info = crypto.obter_saldo(usuario_nome)

    return {
        "pode_buscar": pode_buscar,
        "saldo_atual": saldo_info["saldo"],
        "custo_busca": CryptoManager.CUSTO_BUSCA,
        "mensagem": "Saldo suficiente!" if pode_buscar else "Saldo insuficiente. Adicione preços para ganhar tokens!"
    }


@app.get("/api/economia-token/info")
async def informacoes_economia_token():
    """Informações sobre o sistema de economia de tokens"""
    return {
        "nome": "PreçoCoin",
        "simbolo": "PRC",
        "descricao": "Token de recompensa do Comparador de Preços",
        "economia": {
            "recompensas": {
                "contribuicao_preco": f"{CryptoManager.RECOMPENSA_CONTRIBUICAO} tokens",
                "bonus_cadastro": f"{CryptoManager.BONUS_PRIMEIRO_ACESSO} tokens"
            },
            "custos": {
                "busca_produto": f"{CryptoManager.CUSTO_BUSCA} token"
            }
        },
        "como_ganhar": [
            "Cadastre-se e ganhe 5 tokens de bônus",
            "Adicione preços de produtos e ganhe 10 tokens por contribuição",
            "Quanto mais você contribui, mais você pode buscar!"
        ],
        "como_usar": [
            "Use 1 token por busca de produto",
            "Acumule tokens contribuindo com preços"
        ]
    }


@app.get("/api/ranking-mineradores")
async def ranking_mineradores(
    limite: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Ranking dos maiores mineradores (contribuidores)"""
    from sqlalchemy import desc

    # Top carteiras por saldo
    top_carteiras = db.query(Carteira).order_by(
        desc(Carteira.saldo)
    ).limit(limite).all()

    ranking = []
    for idx, carteira in enumerate(top_carteiras, 1):
        crypto = CryptoManager(db)
        stats = crypto.obter_saldo(carteira.usuario_nome)

        ranking.append({
            "posicao": idx,
            "usuario": carteira.usuario_nome,
            "saldo": carteira.saldo,
            "total_minerado": stats["total_minerado"],
            "total_transacoes": stats["total_transacoes"]
        })

    return {
        "total": len(ranking),
        "ranking": ranking
    }


# ============================================
# ENDPOINTS DO SISTEMA DAO
# ============================================

# -------- COMENTÁRIOS --------

@app.post("/api/dao/comentarios", response_model=ComentarioResponse)
async def criar_comentario(
    comentario: ComentarioCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um comentário na comunidade
    +0.5 reputação (máximo 5 comentários por dia)
    """
    if not comentario.usuario_nome or not comentario.conteudo.strip():
        raise HTTPException(status_code=400, detail="Usuário e conteúdo são obrigatórios")

    novo_comentario = Comentario(
        usuario_nome=comentario.usuario_nome,
        conteudo=comentario.conteudo.strip()
    )
    db.add(novo_comentario)
    db.commit()
    db.refresh(novo_comentario)

    # Dar reputação por comentário (limitado)
    from app.utils.crypto_manager import ReputacaoManager
    rep_manager = ReputacaoManager(db)
    if rep_manager.pode_ganhar_reputacao_comentario(comentario.usuario_nome):
        rep_manager.adicionar_reputacao(
            comentario.usuario_nome,
            ReputacaoManager.COMENTARIO_DAO,
            "Comentário na DAO"
        )

    return novo_comentario


@app.get("/api/dao/comentarios")
async def listar_comentarios(
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    usuario_atual: str = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Lista comentários da comunidade (mais recentes primeiro)
    Inclui informações de votos e reputação do autor
    """
    from app.models.database import VotoComentario, Carteira
    from sqlalchemy import func

    comentarios = db.query(Comentario).order_by(
        Comentario.data_criacao.desc()
    ).offset(offset).limit(limite).all()

    resultado = []
    for c in comentarios:
        # Contar likes e dislikes
        likes = db.query(func.count(VotoComentario.id)).filter(
            VotoComentario.comentario_id == c.id,
            VotoComentario.tipo == "like"
        ).scalar() or 0

        dislikes = db.query(func.count(VotoComentario.id)).filter(
            VotoComentario.comentario_id == c.id,
            VotoComentario.tipo == "dislike"
        ).scalar() or 0

        # Verificar se usuário atual já votou
        voto_usuario = None
        if usuario_atual:
            voto_obj = db.query(VotoComentario).filter(
                VotoComentario.comentario_id == c.id,
                VotoComentario.usuario_nome == usuario_atual
            ).first()
            if voto_obj:
                voto_usuario = voto_obj.tipo

        # Buscar reputação do autor
        carteira = db.query(Carteira).filter(
            Carteira.usuario_nome == c.usuario_nome
        ).first()
        reputacao = carteira.reputacao if carteira else 100

        resultado.append({
            "id": c.id,
            "usuario_nome": c.usuario_nome,
            "conteudo": c.conteudo,
            "data_criacao": c.data_criacao,
            "editado": c.editado,
            "data_edicao": c.data_edicao,
            "likes": likes,
            "dislikes": dislikes,
            "voto_usuario": voto_usuario,
            "reputacao_autor": reputacao
        })

    return resultado


@app.delete("/api/dao/comentarios/{comentario_id}")
async def deletar_comentario(
    comentario_id: int,
    usuario_nome: str,
    db: Session = Depends(get_db)
):
    """
    Deleta um comentário (apenas o autor ou admin pode deletar)
    """
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()

    if not comentario:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")

    # Apenas o autor ou admin pode deletar
    if comentario.usuario_nome != usuario_nome and usuario_nome != "Vengel":
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este comentário")

    db.delete(comentario)
    db.commit()

    return {"message": "Comentário deletado com sucesso"}


@app.post("/api/dao/comentarios/{comentario_id}/votar")
async def votar_comentario(
    comentario_id: int,
    usuario_nome: str = Query(...),
    tipo: str = Query(..., regex="^(like|dislike)$"),
    db: Session = Depends(get_db)
):
    """
    Vota (like/dislike) em um comentário

    Regras:
    - Um usuário só pode votar uma vez por comentário
    - Pode mudar o voto (de like para dislike ou vice-versa)
    - A reputação do autor é recalculada automaticamente
    """
    from app.models.database import VotoComentario
    from app.utils.crypto_manager import ReputacaoManager

    # Verificar se comentário existe
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")

    # Verificar se já votou
    voto_existente = db.query(VotoComentario).filter(
        VotoComentario.comentario_id == comentario_id,
        VotoComentario.usuario_nome == usuario_nome
    ).first()

    if voto_existente:
        # Se já votou do mesmo tipo, remove o voto
        if voto_existente.tipo == tipo:
            db.delete(voto_existente)
            db.commit()
            mensagem = "Voto removido"
        else:
            # Muda o voto
            voto_existente.tipo = tipo
            voto_existente.data_voto = datetime.now()
            db.commit()
            mensagem = f"Voto alterado para {tipo}"
    else:
        # Novo voto
        novo_voto = VotoComentario(
            comentario_id=comentario_id,
            usuario_nome=usuario_nome,
            tipo=tipo
        )
        db.add(novo_voto)
        db.commit()
        mensagem = f"Voto registrado: {tipo}"

    # Recalcular reputação do autor do comentário
    rep_manager = ReputacaoManager(db)
    resultado_rep = rep_manager.calcular_reputacao_comentario(comentario_id)

    # Contar votos atuais
    from sqlalchemy import func
    likes = db.query(func.count(VotoComentario.id)).filter(
        VotoComentario.comentario_id == comentario_id,
        VotoComentario.tipo == "like"
    ).scalar() or 0

    dislikes = db.query(func.count(VotoComentario.id)).filter(
        VotoComentario.comentario_id == comentario_id,
        VotoComentario.tipo == "dislike"
    ).scalar() or 0

    return {
        "mensagem": mensagem,
        "likes": likes,
        "dislikes": dislikes,
        "reputacao_atualizada": resultado_rep
    }


# -------- SUGESTÕES --------

@app.post("/api/dao/sugestoes", response_model=SugestaoResponse)
async def criar_sugestao(
    sugestao: SugestaoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma sugestão (fica pendente de aprovação)
    Custo: 5 tokens
    """
    if not sugestao.usuario_nome or not sugestao.titulo.strip() or not sugestao.descricao.strip():
        raise HTTPException(status_code=400, detail="Todos os campos são obrigatórios")

    # Cobrar 5 tokens para criar sugestão
    crypto = CryptoManager(db)
    saldo_info = crypto.obter_saldo(sugestao.usuario_nome)

    if saldo_info["saldo"] < 5:
        raise HTTPException(
            status_code=402,
            detail={
                "mensagem": f"Saldo insuficiente! Você tem {saldo_info['saldo']} tokens e precisa de 5 tokens para criar uma sugestão.",
                "dica": "Contribua com preços para ganhar mais tokens!"
            }
        )

    # Gastar tokens
    resultado = crypto.gastar_tokens(
        sugestao.usuario_nome,
        custo=5,
        descricao="Criação de sugestão na DAO"
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=402, detail=resultado["mensagem"])

    # Criar sugestão
    nova_sugestao = Sugestao(
        usuario_nome=sugestao.usuario_nome,
        titulo=sugestao.titulo.strip(),
        descricao=sugestao.descricao.strip(),
        status=StatusSugestao.PENDENTE_APROVACAO
    )
    db.add(nova_sugestao)
    db.commit()
    db.refresh(nova_sugestao)

    return nova_sugestao


@app.get("/api/dao/sugestoes", response_model=List[SugestaoResponse])
async def listar_sugestoes(
    status: Optional[str] = None,
    usuario_nome: Optional[str] = None,
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lista sugestões (pode filtrar por status e/ou usuário)
    """
    query = db.query(Sugestao)

    if status:
        query = query.filter(Sugestao.status == status)

    if usuario_nome:
        query = query.filter(Sugestao.usuario_nome == usuario_nome)

    sugestoes = query.order_by(Sugestao.data_criacao.desc()).offset(offset).limit(limite).all()

    return sugestoes


@app.get("/api/dao/sugestoes/{sugestao_id}", response_model=SugestaoDetalhadaResponse)
async def obter_sugestao(
    sugestao_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de uma sugestão específica
    """
    sugestao = db.query(Sugestao).filter(Sugestao.id == sugestao_id).first()

    if not sugestao:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")

    # Contar quantos usuários votaram
    votos_count = db.query(func.count(func.distinct(Voto.usuario_nome))).filter(
        Voto.sugestao_id == sugestao_id
    ).scalar()

    # Lista de aprovadores
    aprovadores_lista = sugestao.aprovadores.split(",") if sugestao.aprovadores else []

    return SugestaoDetalhadaResponse(
        **sugestao.__dict__,
        aprovadores_lista=aprovadores_lista,
        total_usuarios_votaram=votos_count or 0
    )


@app.post("/api/dao/sugestoes/{sugestao_id}/aprovar")
async def aprovar_sugestao(
    sugestao_id: int,
    request: AprovarSugestaoRequest,
    db: Session = Depends(get_db)
):
    """
    Aprova uma sugestão para entrar em votação
    Precisa de pelo menos 1 aprovação de usuário da comunidade
    """
    sugestao = db.query(Sugestao).filter(Sugestao.id == sugestao_id).first()

    if not sugestao:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")

    if sugestao.status != StatusSugestao.PENDENTE_APROVACAO:
        raise HTTPException(status_code=400, detail="Sugestão não está pendente de aprovação")

    # Verificar se usuário já aprovou
    aprovadores_lista = sugestao.aprovadores.split(",") if sugestao.aprovadores else []

    if request.usuario_nome in aprovadores_lista:
        raise HTTPException(status_code=400, detail="Você já aprovou esta sugestão")

    # Adicionar aprovador
    aprovadores_lista.append(request.usuario_nome)
    sugestao.aprovadores = ",".join(aprovadores_lista)
    sugestao.total_aprovadores = len(aprovadores_lista)

    # Se você (Vengel) ou qualquer usuário aprovar, vai para votação
    # Pode ajustar lógica aqui se quiser exigir mais aprovações
    if request.usuario_nome == "Vengel" or sugestao.total_aprovadores >= 1:
        sugestao.status = StatusSugestao.EM_VOTACAO
        sugestao.data_aprovacao = datetime.now()

    db.commit()
    db.refresh(sugestao)

    return {
        "sucesso": True,
        "mensagem": "Sugestão aprovada!" if sugestao.status == StatusSugestao.EM_VOTACAO else "Aprovação registrada. Aguardando mais aprovações.",
        "sugestao": sugestao
    }


@app.post("/api/dao/sugestoes/{sugestao_id}/rejeitar")
async def rejeitar_sugestao(
    sugestao_id: int,
    request: RejeitarSugestaoRequest,
    db: Session = Depends(get_db)
):
    """
    Rejeita uma sugestão (apenas admin)
    """
    if request.usuario_admin != "Vengel":
        raise HTTPException(status_code=403, detail="Apenas o admin pode rejeitar sugestões")

    sugestao = db.query(Sugestao).filter(Sugestao.id == sugestao_id).first()

    if not sugestao:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")

    sugestao.status = StatusSugestao.REJEITADA
    sugestao.motivo_rejeicao = request.motivo
    sugestao.data_finalizacao = datetime.now()

    db.commit()

    return {
        "sucesso": True,
        "mensagem": "Sugestão rejeitada",
        "sugestao": sugestao
    }


# -------- VOTAÇÃO --------

@app.post("/api/dao/votar", response_model=ResultadoVotacao)
async def votar_sugestao(
    voto: VotoCreate,
    db: Session = Depends(get_db)
):
    """
    Vota em uma sugestão usando votação quadrática
    Fórmula: votos = sqrt(tokens)
    Exemplo: 4 tokens = 2 votos, 9 tokens = 3 votos, 16 tokens = 4 votos
    """
    import math

    # Buscar sugestão
    sugestao = db.query(Sugestao).filter(Sugestao.id == voto.sugestao_id).first()

    if not sugestao:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")

    if sugestao.status != StatusSugestao.EM_VOTACAO:
        raise HTTPException(status_code=400, detail="Esta sugestão não está em votação")

    # Verificar se usuário já votou
    voto_existente = db.query(Voto).filter(
        Voto.sugestao_id == voto.sugestao_id,
        Voto.usuario_nome == voto.usuario_nome
    ).first()

    if voto_existente:
        raise HTTPException(status_code=400, detail="Você já votou nesta sugestão")

    # Verificar saldo
    crypto = CryptoManager(db)
    saldo_info = crypto.obter_saldo(voto.usuario_nome)

    if saldo_info["saldo"] < voto.tokens_usados:
        raise HTTPException(
            status_code=402,
            detail=f"Saldo insuficiente. Você tem {saldo_info['saldo']} tokens e precisa de {voto.tokens_usados}"
        )

    # Calcular votos gerados (votação quadrática)
    votos_gerados = int(math.sqrt(voto.tokens_usados))

    # Gastar tokens
    resultado_gasto = crypto.gastar_tokens(
        voto.usuario_nome,
        custo=voto.tokens_usados,
        descricao=f"Voto na sugestão #{voto.sugestao_id}"
    )

    if not resultado_gasto["sucesso"]:
        raise HTTPException(status_code=402, detail=resultado_gasto["mensagem"])

    # Registrar voto
    novo_voto = Voto(
        sugestao_id=voto.sugestao_id,
        usuario_nome=voto.usuario_nome,
        tokens_usados=voto.tokens_usados,
        votos_gerados=votos_gerados,
        voto_favor=voto.voto_favor
    )
    db.add(novo_voto)

    # Atualizar contadores da sugestão
    if voto.voto_favor:
        sugestao.total_votos_favor += votos_gerados
    else:
        sugestao.total_votos_contra += votos_gerados

    sugestao.total_tokens_votados += voto.tokens_usados

    # Calcular porcentagem
    total_votos = sugestao.total_votos_favor + sugestao.total_votos_contra
    if total_votos > 0:
        sugestao.porcentagem_aprovacao = (sugestao.total_votos_favor / total_votos) * 100
    else:
        sugestao.porcentagem_aprovacao = 0

    # Verificar se atingiu 60% de aprovação (com mínimo de 10 votos)
    if total_votos >= 10 and sugestao.porcentagem_aprovacao >= 60:
        sugestao.status = StatusSugestao.APROVADA
        sugestao.data_finalizacao = datetime.now()

        # Dar reputação ao criador da sugestão aprovada
        from app.utils.crypto_manager import ReputacaoManager
        rep_manager = ReputacaoManager(db)
        rep_manager.adicionar_reputacao(
            sugestao.usuario_nome,
            ReputacaoManager.SUGESTAO_APROVADA,
            f"Sugestão #{sugestao.id} aprovada pela comunidade"
        )

    # Dar reputação por participar da votação
    from app.utils.crypto_manager import ReputacaoManager
    rep_manager = ReputacaoManager(db)
    rep_manager.adicionar_reputacao(
        voto.usuario_nome,
        ReputacaoManager.VOTO_SUGESTAO,
        f"Voto na sugestão #{voto.sugestao_id}"
    )

    db.commit()
    db.refresh(sugestao)

    return ResultadoVotacao(
        sucesso=True,
        mensagem=f"Voto registrado! {votos_gerados} voto(s) {'a favor' if voto.voto_favor else 'contra'} (+{ReputacaoManager.VOTO_SUGESTAO} reputação)",
        tokens_gastos=voto.tokens_usados,
        votos_gerados=votos_gerados,
        saldo_restante=resultado_gasto["saldo_atual"],
        sugestao=sugestao
    )


@app.get("/api/dao/sugestoes/{sugestao_id}/votos", response_model=List[VotoResponse])
async def listar_votos_sugestao(
    sugestao_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todos os votos de uma sugestão
    """
    votos = db.query(Voto).filter(Voto.sugestao_id == sugestao_id).order_by(
        Voto.data_voto.desc()
    ).all()

    return votos


# -------- ESTATÍSTICAS --------

@app.get("/api/dao/estatisticas", response_model=EstatisticasDAO)
async def estatisticas_dao(db: Session = Depends(get_db)):
    """
    Estatísticas gerais do sistema DAO
    """
    total_comentarios = db.query(Comentario).count()
    total_sugestoes = db.query(Sugestao).count()

    sugestoes_pendentes = db.query(Sugestao).filter(
        Sugestao.status == StatusSugestao.PENDENTE_APROVACAO
    ).count()

    sugestoes_em_votacao = db.query(Sugestao).filter(
        Sugestao.status == StatusSugestao.EM_VOTACAO
    ).count()

    sugestoes_aprovadas = db.query(Sugestao).filter(
        Sugestao.status == StatusSugestao.APROVADA
    ).count()

    sugestoes_implementadas = db.query(Sugestao).filter(
        Sugestao.status == StatusSugestao.IMPLEMENTADA
    ).count()

    # Usuários que participaram (comentaram, sugeriram ou votaram)
    usuarios_comentarios = db.query(func.count(func.distinct(Comentario.usuario_nome))).scalar() or 0
    usuarios_sugestoes = db.query(func.count(func.distinct(Sugestao.usuario_nome))).scalar() or 0
    usuarios_votos = db.query(func.count(func.distinct(Voto.usuario_nome))).scalar() or 0

    total_usuarios_participantes = len(set([usuarios_comentarios, usuarios_sugestoes, usuarios_votos]))

    # Total de tokens votados
    total_tokens_votados = db.query(func.sum(Voto.tokens_usados)).scalar() or 0

    return EstatisticasDAO(
        total_comentarios=total_comentarios,
        total_sugestoes=total_sugestoes,
        sugestoes_pendentes=sugestoes_pendentes,
        sugestoes_em_votacao=sugestoes_em_votacao,
        sugestoes_aprovadas=sugestoes_aprovadas,
        sugestoes_implementadas=sugestoes_implementadas,
        total_usuarios_participantes=total_usuarios_participantes,
        total_tokens_votados=total_tokens_votados
    )


@app.patch("/api/dao/sugestoes/{sugestao_id}/status")
async def atualizar_status_sugestao(
    sugestao_id: int,
    novo_status: str,
    admin_usuario: str,
    db: Session = Depends(get_db)
):
    """
    Atualiza status de uma sugestão (implementada, rejeitada, etc)
    Apenas usuário Vengel pode fazer isso por enquanto
    """
    # Verificação simples de admin (em produção usar sistema de permissões)
    if admin_usuario != "Vengel":
        raise HTTPException(status_code=403, detail="Apenas administradores podem alterar status")

    sugestao = db.query(Sugestao).filter(Sugestao.id == sugestao_id).first()
    if not sugestao:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")

    # Validar novo status
    try:
        novo_status_enum = StatusSugestao(novo_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Status inválido")

    status_antigo = sugestao.status
    sugestao.status = novo_status_enum
    sugestao.data_finalizacao = datetime.now()

    # Dar reputação baseado no novo status
    from app.utils.crypto_manager import ReputacaoManager
    rep_manager = ReputacaoManager(db)

    if novo_status_enum == StatusSugestao.IMPLEMENTADA:
        rep_manager.adicionar_reputacao(
            sugestao.usuario_nome,
            ReputacaoManager.SUGESTAO_IMPLEMENTADA,
            f"Sugestão #{sugestao.id} foi implementada"
        )
    elif novo_status_enum == StatusSugestao.REJEITADA:
        rep_manager.adicionar_reputacao(
            sugestao.usuario_nome,
            ReputacaoManager.SUGESTAO_REJEITADA,
            f"Sugestão #{sugestao.id} foi rejeitada"
        )

    db.commit()

    return {
        "sucesso": True,
        "mensagem": f"Status atualizado de {status_antigo.value} para {novo_status_enum.value}",
        "sugestao_id": sugestao.id,
        "novo_status": novo_status_enum.value
    }


# ============================================
# ENDPOINTS DO SISTEMA DE REPUTAÇÃO
# ============================================

@app.get("/api/reputacao/contribuicoes-pendentes", response_model=List[ContribuicaoParaValidar])
async def listar_contribuicoes_pendentes(
    usuario_nome: str,
    limite: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista contribuições de preços que precisam de validação
    Exclui as próprias contribuições do usuário
    """
    # Buscar preços manuais recentes (últimos 7 dias)
    data_limite = datetime.now() - timedelta(days=7)

    precos = db.query(Preco).join(Produto).filter(
        Preco.manual == True,
        Preco.usuario_nome != usuario_nome,  # Não mostrar suas próprias
        Preco.data_coleta >= data_limite
    ).order_by(Preco.data_coleta.desc()).limit(limite).all()

    resultado = []
    for preco in precos:
        # Contar validações deste preço
        validacoes = db.query(ValidacaoPreco).filter(
            ValidacaoPreco.preco_id == preco.id
        ).all()

        aprovacoes = sum(1 for v in validacoes if v.aprovado)
        rejeicoes = sum(1 for v in validacoes if not v.aprovado)

        # Buscar reputação do autor
        carteira_autor = db.query(Carteira).filter(
            Carteira.usuario_nome == preco.usuario_nome
        ).first()

        reputacao_autor = carteira_autor.reputacao if carteira_autor else 100

        # Verificar se usuário já validou
        ja_validou = db.query(ValidacaoPreco).filter(
            ValidacaoPreco.preco_id == preco.id,
            ValidacaoPreco.validador_nome == usuario_nome
        ).first()

        if not ja_validou:  # Só mostra se ainda não validou
            resultado.append(ContribuicaoParaValidar(
                preco_id=preco.id,
                produto_nome=preco.produto.nome,
                produto_marca=preco.produto.marca,
                preco=preco.preco,
                supermercado=preco.supermercado,
                usuario_nome=preco.usuario_nome,
                usuario_reputacao=reputacao_autor,
                localizacao=preco.localizacao,
                data_coleta=preco.data_coleta,
                total_validacoes=len(validacoes),
                aprovacoes=aprovacoes,
                rejeicoes=rejeicoes,
                precisa_validacao=len(validacoes) < 3  # Precisa de pelo menos 3 validações
            ))

    return resultado


@app.post("/api/reputacao/validar", response_model=ValidacaoResponse)
async def validar_contribuicao(
    validacao: ValidarPrecoRequest,
    db: Session = Depends(get_db)
):
    """
    Valida uma contribuição de preço
    Atualiza reputação do autor baseado no consenso
    """
    # Buscar o preço
    preco = db.query(Preco).filter(Preco.id == validacao.preco_id).first()

    if not preco:
        raise HTTPException(status_code=404, detail="Preço não encontrado")

    # Não pode validar própria contribuição
    if preco.usuario_nome == validacao.validador_nome:
        raise HTTPException(status_code=400, detail="Você não pode validar sua própria contribuição")

    # Verificar se já validou
    validacao_existente = db.query(ValidacaoPreco).filter(
        ValidacaoPreco.preco_id == validacao.preco_id,
        ValidacaoPreco.validador_nome == validacao.validador_nome
    ).first()

    if validacao_existente:
        raise HTTPException(status_code=400, detail="Você já validou esta contribuição")

    # Calcular diferença percentual se foi rejeitado
    diferenca_percentual = None
    if not validacao.aprovado and validacao.preco_sugerido:
        if preco.preco > 0:
            diferenca_percentual = abs((validacao.preco_sugerido - preco.preco) / preco.preco) * 100

    # Criar validação
    nova_validacao = ValidacaoPreco(
        preco_id=validacao.preco_id,
        validador_nome=validacao.validador_nome,
        validado_nome=preco.usuario_nome,
        aprovado=validacao.aprovado,
        motivo=validacao.motivo,
        preco_sugerido=validacao.preco_sugerido,
        diferenca_percentual=diferenca_percentual
    )
    db.add(nova_validacao)

    # Atualizar contador de validações feitas do validador
    carteira_validador = db.query(Carteira).filter(
        Carteira.usuario_nome == validacao.validador_nome
    ).first()
    if carteira_validador:
        carteira_validador.total_validacoes_feitas += 1

    # Atualizar reputação do autor
    atualizar_reputacao_autor(db, preco.id, preco.usuario_nome)

    db.commit()
    db.refresh(nova_validacao)

    return nova_validacao


def atualizar_reputacao_autor(db: Session, preco_id: int, usuario_nome: str):
    """
    Atualiza reputação do autor baseado nas validações recebidas
    Sistema de consenso: maioria decide
    """
    # Buscar todas as validações deste preço
    validacoes = db.query(ValidacaoPreco).filter(
        ValidacaoPreco.preco_id == preco_id
    ).all()

    if len(validacoes) < 2:  # Precisa de pelo menos 2 validações
        return

    aprovacoes = sum(1 for v in validacoes if v.aprovado)
    rejeicoes = sum(1 for v in validacoes if not v.aprovado)
    total = len(validacoes)

    # Buscar carteira do autor
    carteira = db.query(Carteira).filter(
        Carteira.usuario_nome == usuario_nome
    ).first()

    if not carteira:
        return

    # Atualizar contadores
    carteira.total_validacoes_recebidas = total
    carteira.validacoes_positivas = aprovacoes
    carteira.validacoes_negativas = rejeicoes

    # Calcular mudança de reputação baseado no consenso
    taxa_aprovacao = (aprovacoes / total) * 100

    if taxa_aprovacao >= 70:  # 70%+ de aprovação
        # Ganha reputação
        ganho = 5 * len(validacoes)  # 5 pontos por validação
        carteira.reputacao = min(200, carteira.reputacao + ganho)
    elif taxa_aprovacao <= 30:  # 30%- de aprovação (maioria rejeitou)
        # Perde reputação
        perda = 10 * len(validacoes)  # 10 pontos por validação
        carteira.reputacao = max(0, carteira.reputacao - perda)


@app.get("/api/reputacao/{usuario_nome}", response_model=ReputacaoResponse)
async def obter_reputacao(
    usuario_nome: str,
    db: Session = Depends(get_db)
):
    """
    Obtém informações de reputação de um usuário
    """
    carteira = db.query(Carteira).filter(
        Carteira.usuario_nome == usuario_nome
    ).first()

    if not carteira:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Calcular taxa de aprovação
    taxa_aprovacao = 0.0
    if carteira.total_validacoes_recebidas > 0:
        taxa_aprovacao = (carteira.validacoes_positivas / carteira.total_validacoes_recebidas) * 100

    # Determinar nível de confiança
    if carteira.reputacao >= 150:
        nivel = "Muito Alto"
    elif carteira.reputacao >= 100:
        nivel = "Alto"
    elif carteira.reputacao >= 50:
        nivel = "Médio"
    else:
        nivel = "Baixo"

    return ReputacaoResponse(
        usuario_nome=usuario_nome,
        reputacao=carteira.reputacao,
        total_validacoes_feitas=carteira.total_validacoes_feitas,
        total_validacoes_recebidas=carteira.total_validacoes_recebidas,
        validacoes_positivas=carteira.validacoes_positivas,
        validacoes_negativas=carteira.validacoes_negativas,
        taxa_aprovacao=round(taxa_aprovacao, 1),
        nivel_confianca=nivel
    )


@app.get("/api/reputacao/validacoes/{usuario_nome}", response_model=List[ValidacaoResponse])
async def listar_validacoes_recebidas(
    usuario_nome: str,
    limite: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Lista validações recebidas por um usuário
    """
    validacoes = db.query(ValidacaoPreco).filter(
        ValidacaoPreco.validado_nome == usuario_nome
    ).order_by(ValidacaoPreco.data_validacao.desc()).limit(limite).all()

    return validacoes


# Mount static files AFTER all API routes
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/src", StaticFiles(directory=os.path.join(frontend_path, "src")), name="static-src")
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
