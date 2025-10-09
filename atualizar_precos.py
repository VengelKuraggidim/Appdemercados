#!/usr/bin/env python3
"""
Script de Atualização Automática de Preços
Executa scraping periódico para manter preços atualizados
"""
import sys
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import get_db, Produto, Preco
from app.scrapers.scraper_manager import ScraperManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/atualizacao_precos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def atualizar_precos_produtos():
    """Atualiza preços dos produtos mais buscados"""
    logger.info("="*60)
    logger.info(f"🔄 Iniciando atualização de preços - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)

    db = next(get_db())
    scraper_manager = ScraperManager()

    # Buscar produtos com preços desatualizados (mais de 24h)
    data_limite = datetime.now() - timedelta(hours=24)

    try:
        # Pegar os 20 produtos mais recentes/buscados
        produtos = db.query(Produto).join(Preco).filter(
            Preco.data_coleta < data_limite
        ).group_by(Produto.id).limit(20).all()

        if not produtos:
            logger.info("✅ Nenhum produto precisa de atualização no momento")
            return

        logger.info(f"📦 Encontrados {len(produtos)} produtos para atualizar")

        total_atualizados = 0
        total_novos_precos = 0

        for produto in produtos:
            logger.info(f"🔍 Atualizando: {produto.nome}...")

            try:
                # Fazer scraping do produto
                resultados = scraper_manager.search_all(
                    termo=produto.nome,
                    supermercados=None
                )

                if resultados:
                    for item in resultados:
                        # Verificar se já existe preço recente deste supermercado
                        preco_existente = db.query(Preco).filter(
                            Preco.produto_id == produto.id,
                            Preco.supermercado == item['supermercado'],
                            Preco.data_coleta >= data_limite
                        ).first()

                        if not preco_existente:
                            # Adicionar novo preço
                            novo_preco = Preco(
                                produto_id=produto.id,
                                supermercado=item['supermercado'],
                                preco=item['preco'],
                                em_promocao=item.get('em_promocao', False),
                                url=item.get('url'),
                                disponivel=item.get('disponivel', True),
                                data_coleta=datetime.now(),
                                manual=False
                            )
                            db.add(novo_preco)
                            total_novos_precos += 1
                            logger.info(f"  ✅ {item['supermercado']}: R$ {item['preco']:.2f}")

                    total_atualizados += 1
                    db.commit()
                else:
                    logger.warning(f"  ⚠️  Nenhum resultado encontrado para {produto.nome}")

            except Exception as e:
                logger.error(f"  ❌ Erro ao atualizar {produto.nome}: {str(e)}")
                db.rollback()
                continue

        logger.info("="*60)
        logger.info("📊 Resumo da Atualização:")
        logger.info(f"   • Produtos atualizados: {total_atualizados}")
        logger.info(f"   • Novos preços adicionados: {total_novos_precos}")
        logger.info(f"   • Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"❌ Erro fatal na atualização de preços: {str(e)}")
        raise
    finally:
        db.close()


def atualizar_produtos_principais():
    """Atualiza produtos básicos/principais do mercado"""
    produtos_basicos = [
        "arroz",
        "feijão",
        "açúcar",
        "café",
        "óleo",
        "macarrão",
        "leite",
        "pão"
    ]

    logger.info("="*60)
    logger.info(f"🛒 Atualizando produtos básicos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)

    db = next(get_db())
    scraper_manager = ScraperManager()

    total_precos = 0

    try:
        for termo in produtos_basicos:
            logger.info(f"🔍 Buscando: {termo}...")

            try:
                resultados = scraper_manager.search_all(termo=termo, supermercados=None)

                if resultados:
                    for item in resultados[:3]:  # Top 3 resultados por termo
                        # Buscar ou criar produto
                        produto = db.query(Produto).filter(
                            Produto.nome.ilike(f"%{item['nome'][:50]}%")
                        ).first()

                        if not produto:
                            produto = Produto(
                                nome=item['nome'],
                                marca=item.get('marca'),
                                categoria='basicos'
                            )
                            db.add(produto)
                            db.flush()

                        # Adicionar preço
                        novo_preco = Preco(
                            produto_id=produto.id,
                            supermercado=item['supermercado'],
                            preco=item['preco'],
                            em_promocao=item.get('em_promocao', False),
                            url=item.get('url'),
                            disponivel=item.get('disponivel', True),
                            data_coleta=datetime.now(),
                            manual=False
                        )
                        db.add(novo_preco)
                        total_precos += 1
                        logger.info(f"  ✅ {item['nome'][:40]} - {item['supermercado']}: R$ {item['preco']:.2f}")

                    db.commit()
                else:
                    logger.warning(f"  ⚠️  Nenhum resultado para {termo}")

            except Exception as e:
                logger.error(f"  ❌ Erro ao buscar {termo}: {str(e)}")
                db.rollback()
                continue

        logger.info("="*60)
        logger.info(f"📊 Total de preços adicionados: {total_precos}")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"❌ Erro fatal na atualização de produtos básicos: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Atualizar preços de produtos')
    parser.add_argument(
        '--modo',
        choices=['produtos', 'basicos', 'ambos'],
        default='ambos',
        help='Modo de atualização'
    )

    args = parser.parse_args()

    try:
        if args.modo in ['produtos', 'ambos']:
            atualizar_precos_produtos()

        if args.modo in ['basicos', 'ambos']:
            atualizar_produtos_principais()

        print("✅ Atualização concluída com sucesso!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Atualização cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        sys.exit(1)
