"""
Price Updater Scheduler
Agendador integrado à aplicação para atualização automática de preços
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.models.database import SessionLocal, Produto, Preco
from app.scrapers.scraper_manager import ScraperManager

# Configurar logging
logger = logging.getLogger(__name__)


class PriceUpdater:
    """Gerenciador de atualização automática de preços"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running = False
        self.scraper_manager = ScraperManager()

    def atualizar_precos(self):
        """Atualiza preços dos produtos no banco de dados"""
        logger.info("="*60)
        logger.info(f"🔄 Iniciando atualização automática de preços - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)

        db = SessionLocal()

        try:
            from datetime import timedelta

            # Buscar produtos com preços desatualizados (mais de 24h)
            data_limite = datetime.now() - timedelta(hours=24)

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
                    resultados = self.scraper_manager.search_all(
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
            logger.error(f"❌ Erro fatal na atualização de preços: {str(e)}", exc_info=True)
        finally:
            db.close()

    def start(self, interval_hours: int = 7):
        """
        Inicia o agendador de atualização de preços

        Args:
            interval_hours: Intervalo em horas entre atualizações (padrão: 7)
        """
        if not self.running:
            self.scheduler.add_job(
                self.atualizar_precos,
                trigger=IntervalTrigger(hours=interval_hours),
                id='atualizar_precos_7h',
                name=f'Atualização Automática de Preços ({interval_hours}h)',
                replace_existing=True
            )

            self.scheduler.start()
            self.running = True

            logger.info(f"✅ Agendador de preços iniciado! Atualizando a cada {interval_hours} horas.")

            # Log da próxima execução
            for job in self.scheduler.get_jobs():
                if job.id == 'atualizar_precos_7h':
                    next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A'
                    logger.info(f"📅 Próxima atualização: {next_run}")

    def stop(self):
        """Para o agendador"""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("⏹️  Agendador de preços parado.")


# Instância global
price_updater = PriceUpdater()
