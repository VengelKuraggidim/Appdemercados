#!/usr/bin/env python3
"""
Script para criar o primeiro moderador (Vengel)
"""
from app.models.database import SessionLocal, Moderador

def criar_moderador_inicial():
    db = SessionLocal()

    try:
        # Verificar se já existe
        moderador_existente = db.query(Moderador).filter(
            Moderador.usuario_nome == "Vengel"
        ).first()

        if moderador_existente:
            print("✅ Moderador 'Vengel' já existe!")
            print(f"   Reputação: {moderador_existente.reputacao_moderador}")
            print(f"   Implementadas: {moderador_existente.total_sugestoes_implementadas}")
            return

        # Criar moderador
        moderador = Moderador(
            usuario_nome="Vengel",
            ativo=True,
            reputacao_moderador=100
        )

        db.add(moderador)
        db.commit()
        db.refresh(moderador)

        print("🎉 Moderador criado com sucesso!")
        print(f"   Usuário: {moderador.usuario_nome}")
        print(f"   Reputação: {moderador.reputacao_moderador}")
        print(f"   Ativo: {'✅ Sim' if moderador.ativo else '❌ Não'}")
        print("\n💡 Você agora pode:")
        print("   • Aprovar sugestões para votação")
        print("   • Aceitar implementar sugestões aprovadas")
        print("   • Receber tokens em escrow ao implementar")

    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    criar_moderador_inicial()
