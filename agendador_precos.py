#!/usr/bin/env python3
"""
Agendador Automático de Atualização de Preços
Executa atualizações periódicas usando APScheduler
"""
import sys
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atualizar_precos import atualizar_precos_produtos, atualizar_produtos_principais


def executar_atualizacao_completa():
    """Executa atualização completa"""
    print(f"\n{'='*60}")
    print(f"🤖 ATUALIZAÇÃO AUTOMÁTICA INICIADA")
    print(f"{'='*60}")

    try:
        # Atualizar produtos existentes
        atualizar_precos_produtos()

        # Atualizar produtos básicos
        atualizar_produtos_principais()

        print(f"\n✅ Atualização automática concluída com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro na atualização: {str(e)}")


def executar_atualizacao_rapida():
    """Executa atualização rápida (apenas produtos existentes)"""
    print(f"\n{'='*60}")
    print(f"⚡ ATUALIZAÇÃO RÁPIDA INICIADA")
    print(f"{'='*60}")

    try:
        atualizar_precos_produtos()
        print(f"\n✅ Atualização rápida concluída!")

    except Exception as e:
        print(f"\n❌ Erro na atualização: {str(e)}")


def iniciar_agendador():
    """Inicia o agendador de tarefas"""
    scheduler = BackgroundScheduler()

    # Atualização completa: Todos os dias às 6h e 18h
    scheduler.add_job(
        executar_atualizacao_completa,
        CronTrigger(hour='6,18', minute=0),
        id='atualizacao_completa',
        name='Atualização Completa de Preços',
        replace_existing=True
    )

    # Atualização rápida: A cada 4 horas
    scheduler.add_job(
        executar_atualizacao_rapida,
        CronTrigger(hour='*/4'),
        id='atualizacao_rapida',
        name='Atualização Rápida de Preços',
        replace_existing=True
    )

    scheduler.start()

    print(f"\n{'='*60}")
    print(f"📅 AGENDADOR DE PREÇOS INICIADO")
    print(f"{'='*60}")
    print(f"\n⏰ Tarefas agendadas:")
    print(f"   • Atualização Completa: Diariamente às 6h e 18h")
    print(f"   • Atualização Rápida: A cada 4 horas")
    print(f"\n💡 Próximas execuções:")

    for job in scheduler.get_jobs():
        next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A'
        print(f"   • {job.name}: {next_run}")

    print(f"\n🔄 Agendador rodando... (Ctrl+C para parar)")
    print(f"{'='*60}\n")

    return scheduler


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Agendador de atualização de preços')
    parser.add_argument(
        '--executar-agora',
        action='store_true',
        help='Executar atualização imediatamente antes de iniciar o agendador'
    )

    args = parser.parse_args()

    try:
        # Executar imediatamente se solicitado
        if args.executar_agora:
            print("🚀 Executando atualização inicial...")
            executar_atualizacao_completa()

        # Iniciar agendador
        scheduler = iniciar_agendador()

        # Manter o programa rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Encerrando agendador...")
            scheduler.shutdown()
            print("✅ Agendador encerrado com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        sys.exit(1)
