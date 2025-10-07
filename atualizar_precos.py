#!/usr/bin/env python3
"""
Script de Atualização Automática de Preços
Executa scraping periódico para manter preços atualizados
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import get_db, Produto, Preco
from app.scrapers.scraper_manager import ScraperManager


def atualizar_precos_produtos():
    """Atualiza preços dos produtos mais buscados"""
    print(f"\n{'='*60}")
    print(f"🔄 Iniciando atualização de preços - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    db = next(get_db())
    scraper_manager = ScraperManager()

    # Buscar produtos com preços desatualizados (mais de 24h)
    data_limite = datetime.now() - timedelta(hours=24)

    # Pegar os 20 produtos mais recentes/buscados
    produtos = db.query(Produto).join(Preco).filter(
        Preco.data_coleta < data_limite
    ).group_by(Produto.id).limit(20).all()

    if not produtos:
        print("✅ Nenhum produto precisa de atualização no momento")
        return

    print(f"📦 Encontrados {len(produtos)} produtos para atualizar\n")

    total_atualizados = 0
    total_novos_precos = 0

    for produto in produtos:
        print(f"🔍 Atualizando: {produto.nome}...")

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
                        print(f"  ✅ {item['supermercado']}: R$ {item['preco']:.2f}")

                total_atualizados += 1
                db.commit()
            else:
                print(f"  ⚠️  Nenhum resultado encontrado")

        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            continue

    print(f"\n{'='*60}")
    print(f"📊 Resumo da Atualização:")
    print(f"   • Produtos atualizados: {total_atualizados}")
    print(f"   • Novos preços adicionados: {total_novos_precos}")
    print(f"   • Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

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

    print(f"\n{'='*60}")
    print(f"🛒 Atualizando produtos básicos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    db = next(get_db())
    scraper_manager = ScraperManager()

    total_precos = 0

    for termo in produtos_basicos:
        print(f"\n🔍 Buscando: {termo}...")

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
                    print(f"  ✅ {item['nome'][:40]} - {item['supermercado']}: R$ {item['preco']:.2f}")

                db.commit()
            else:
                print(f"  ⚠️  Nenhum resultado")

        except Exception as e:
            print(f"  ❌ Erro: {str(e)}")
            continue

    print(f"\n{'='*60}")
    print(f"📊 Total de preços adicionados: {total_precos}")
    print(f"{'='*60}\n")

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
