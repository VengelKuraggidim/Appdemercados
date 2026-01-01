from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from app.models.database import SessionLocal
from app.utils.alertas import AlertaManager


class AlertScheduler:
    """Background scheduler for checking price alerts"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running = False

    def verificar_alertas_job(self):
        """Job that runs periodically to check alerts"""
        print(f"[{datetime.now()}] Verificando alertas de preços...")

        db = SessionLocal()
        try:
            alerta_manager = AlertaManager(db)
            alertas_disparados = alerta_manager.verificar_alertas()

            if alertas_disparados:
                print(f"✓ {len(alertas_disparados)} alertas disparados!")
                for alerta in alertas_disparados:
                    alerta_manager.enviar_notificacao(alerta)
            else:
                print("✓ Nenhum alerta disparado.")

        except Exception as e:
            print(f"✗ Erro ao verificar alertas: {e}")
        finally:
            db.close()

    def start(self, interval_minutes: int = 60):
        """Start the scheduler"""
        if not self.running:
            self.scheduler.add_job(
                self.verificar_alertas_job,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='verificar_alertas',
                name='Verificar Alertas de Preços',
                replace_existing=True
            )
            self.scheduler.start()
            self.running = True
            print(f"✓ Scheduler iniciado! Verificando alertas a cada {interval_minutes} minutos.")

    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            print("✓ Scheduler parado.")
