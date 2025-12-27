#!/usr/bin/env python3
"""
Script para aplicar aprovação automática a sugestões em votação
que já atingiram 60% de aprovação
"""

from app.models.database import SessionLocal, Sugestao, StatusSugestao
from datetime import datetime

def aplicar_aprovacao_automatica():
    db = SessionLocal()
    try:
        # Buscar todas as sugestões em votação
        sugestoes = db.query(Sugestao).filter(
            Sugestao.status == StatusSugestao.EM_VOTACAO
        ).all()

        aprovadas = 0
        for sugestao in sugestoes:
            total_votos = sugestao.total_votos_favor + sugestao.total_votos_contra

            # Aplicar lógica de aprovação automática (60% com mínimo de 1 voto)
            if total_votos >= 1 and sugestao.porcentagem_aprovacao >= 60:
                print(f"✅ Aprovando sugestão #{sugestao.id}: '{sugestao.titulo}'")
                print(f"   Aprovação: {sugestao.porcentagem_aprovacao:.1f}% ({total_votos} votos)")

                sugestao.status = StatusSugestao.APROVADA
                sugestao.data_aprovacao = datetime.now()
                aprovadas += 1

        db.commit()

        print(f"\n✅ {aprovadas} sugestão(ões) aprovada(s) automaticamente!")

    finally:
        db.close()

if __name__ == "__main__":
    aplicar_aprovacao_automatica()
