#!/usr/bin/env python3
"""
Script de teste para o agendador de atualização de preços
"""
import sys
import os
import time
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.price_updater import price_updater

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_agendador():
    """Testa o agendador de atualização de preços"""
    print("\n" + "="*60)
    print("🧪 TESTE DO AGENDADOR DE ATUALIZAÇÃO DE PREÇOS")
    print("="*60 + "\n")

    try:
        # Iniciar o agendador (a cada 7 horas)
        logger.info("Iniciando agendador...")
        price_updater.start(interval_hours=7)

        # Verificar se está rodando
        if price_updater.running:
            logger.info("✅ Agendador iniciado com sucesso!")
            logger.info(f"   Status: {'RODANDO' if price_updater.running else 'PARADO'}")

            # Mostrar jobs agendados
            jobs = price_updater.scheduler.get_jobs()
            logger.info(f"   Jobs agendados: {len(jobs)}")

            for job in jobs:
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A'
                logger.info(f"   • {job.name}")
                logger.info(f"     Próxima execução: {next_run}")

            # Executar atualização manualmente para testar
            logger.info("\n🔄 Executando atualização manual para teste...")
            price_updater.atualizar_precos()

            logger.info("\n✅ Teste concluído com sucesso!")
            logger.info("💡 O agendador continuará rodando e atualizará os preços a cada 7 horas.")
            logger.info("⚠️  Para usar em produção, inicie a aplicação FastAPI normalmente.")

        else:
            logger.error("❌ Falha ao iniciar o agendador")

    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}", exc_info=True)
        return False
    finally:
        # Parar o agendador após o teste
        logger.info("\n⏹️  Parando agendador...")
        price_updater.stop()

    print("\n" + "="*60)
    print("✅ TESTE FINALIZADO")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    success = test_agendador()
    sys.exit(0 if success else 1)
