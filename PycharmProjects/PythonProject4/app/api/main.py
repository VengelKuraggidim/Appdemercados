from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
import os

from app.models.database import get_db, init_db, Produto, Preco, Alerta, Carteira, Transacao
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
        "recompensa": recompensa
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
    usuario_nome: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    endereco: Optional[str] = None,
    dados_manuais: Optional[str] = None,  # JSON string via FormData
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
                total_tokens_ganhos += recompensa['tokens_minerados']

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
        texto = ocr.extrair_texto(contents)

        # Tentar identificar supermercado e data
        supermercado = ocr.identificar_supermercado(texto)
        data_compra = ocr.extrair_data(texto)
        produtos = ocr.extrair_produtos(texto)
        total = ocr.extrair_total(texto)

        return {
            "texto_completo": texto,
            "total_linhas": len(texto.split('\n')),
            "supermercado_identificado": supermercado,
            "data_identificada": data_compra.isoformat() if data_compra else None,
            "produtos_encontrados": len(produtos),
            "produtos": produtos[:5],  # Primeiros 5
            "total_encontrado": total,
            "primeiras_30_linhas": texto.split('\n')[:30]
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
    """
    if not termo or len(termo.strip()) < 2:
        raise HTTPException(status_code=400, detail="Termo de busca muito curto")

    # Buscar produtos no banco
    data_limite = datetime.now() - timedelta(days=30)

    query = db.query(Preco).join(Produto).filter(
        Produto.nome.ilike(f"%{termo}%"),
        Preco.data_coleta >= data_limite,
        Preco.disponivel == True,
        Preco.latitude.isnot(None),
        Preco.longitude.isnot(None)
    )

    if supermercados:
        query = query.filter(Preco.supermercado.in_(supermercados))

    precos = query.all()

    if not precos:
        return {
            "termo": termo,
            "total": 0,
            "produtos": [],
            "message": "Nenhum produto encontrado com localização cadastrada"
        }

    # Preparar dados para análise
    precos_com_localizacao = []
    for preco in precos:
        precos_com_localizacao.append({
            "id": preco.id,
            "nome": preco.produto.nome,
            "marca": preco.produto.marca,
            "preco": preco.preco,
            "supermercado": preco.supermercado,
            "em_promocao": preco.em_promocao,
            "latitude": preco.latitude,
            "longitude": preco.longitude,
            "endereco": preco.endereco,
            "localizacao": preco.localizacao,
            "data_coleta": preco.data_coleta.isoformat() if preco.data_coleta else None
        })

    # Ranquear por custo-benefício
    resultados = ranquear_precos_por_custo_beneficio(
        precos_com_localizacao,
        latitude,
        longitude,
        tipo_transporte,
        considerar_tempo
    )

    return {
        "termo": termo,
        "total": len(resultados),
        "usuario": {
            "latitude": latitude,
            "longitude": longitude,
            "tipo_transporte": tipo_transporte
        },
        "produtos": resultados
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


# Mount static files AFTER all API routes
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/src", StaticFiles(directory=os.path.join(frontend_path, "src")), name="static-src")
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
