from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import Alerta, Preco, Produto


class AlertaManager:
    """Manager for price alerts"""

    def __init__(self, db: Session):
        self.db = db

    def verificar_alertas(self) -> List[dict]:
        """
        Check all active alerts and return triggered ones
        """
        alertas_disparados = []

        # Get all active alerts
        alertas = self.db.query(Alerta).filter(Alerta.ativo == True).all()

        for alerta in alertas:
            # Get latest price for the product
            preco_recente = self.db.query(Preco).filter(
                Preco.produto_id == alerta.produto_id,
                Preco.disponivel == True,
                Preco.data_coleta >= datetime.now() - timedelta(hours=24)
            ).order_by(Preco.preco.asc()).first()

            if preco_recente and preco_recente.preco <= alerta.preco_alvo:
                # Check if we haven't notified recently (avoid spam)
                if not alerta.data_ultima_notificacao or \
                   (datetime.now() - alerta.data_ultima_notificacao) > timedelta(hours=12):

                    alertas_disparados.append({
                        'alerta_id': alerta.id,
                        'produto': preco_recente.produto.nome,
                        'preco_alvo': alerta.preco_alvo,
                        'preco_encontrado': preco_recente.preco,
                        'supermercado': preco_recente.supermercado.value,
                        'url': preco_recente.url,
                        'economia': alerta.preco_alvo - preco_recente.preco,
                        'email': alerta.email
                    })

                    # Update last notification time
                    alerta.data_ultima_notificacao = datetime.now()

        self.db.commit()
        return alertas_disparados

    def criar_alerta(self, produto_id: int, preco_alvo: float, email: str = None) -> Alerta:
        """Create a new price alert"""
        alerta = Alerta(
            produto_id=produto_id,
            preco_alvo=preco_alvo,
            email=email,
            ativo=True,
            data_criacao=datetime.now()
        )
        self.db.add(alerta)
        self.db.commit()
        self.db.refresh(alerta)
        return alerta

    def desativar_alerta(self, alerta_id: int) -> bool:
        """Deactivate an alert"""
        alerta = self.db.query(Alerta).filter(Alerta.id == alerta_id).first()
        if alerta:
            alerta.ativo = False
            self.db.commit()
            return True
        return False

    def enviar_notificacao(self, alerta_info: dict):
        """
        Send notification (email, push, etc.)
        For now, just print to console
        """
        print(f"""
        ═══════════════════════════════════════════════
        🔔 ALERTA DE PREÇO DISPARADO!
        ═══════════════════════════════════════════════
        Produto: {alerta_info['produto']}
        Preço Alvo: R$ {alerta_info['preco_alvo']:.2f}
        Preço Encontrado: R$ {alerta_info['preco_encontrado']:.2f}
        Supermercado: {alerta_info['supermercado'].upper()}
        Economia: R$ {alerta_info['economia']:.2f}

        Link: {alerta_info['url']}
        ═══════════════════════════════════════════════
        """)

        # TODO: Implement actual email/push notification
        # if alerta_info['email']:
        #     send_email(alerta_info['email'], alerta_info)
