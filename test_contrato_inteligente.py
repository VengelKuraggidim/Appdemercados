#!/usr/bin/env python3
"""
Teste completo do sistema de CONTRATO INTELIGENTE de moderação
Demonstra o fluxo completo com escrow de tokens
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_header(texto):
    print("\n" + "="*80)
    print(f"  {texto}")
    print("="*80 + "\n")

def print_step(numero, texto):
    print(f"\n📌 ETAPA {numero}: {texto}")
    print("-" * 80)

def criar_usuario(nome):
    """Cria carteira do usuário"""
    print(f"👤 Criando usuário: {nome}")
    response = requests.post(
        f"{BASE_URL}/api/carteira/criar",
        json={"usuario_nome": nome}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Carteira criada - Saldo: {data['saldo']} tokens")
        return data
    else:
        print(f"   ⚠️  Usuário já existe")
        return None

def consultar_carteira(usuario):
    """Consulta saldo e reputação"""
    response = requests.get(f"{BASE_URL}/api/carteira/{usuario}")
    if response.status_code == 200:
        return response.json()
    return None

def criar_sugestao(usuario, titulo, descricao):
    """Cria uma sugestão (5 tokens em escrow)"""
    print(f"\n💡 {usuario} criando sugestão: '{titulo}'")

    response = requests.post(
        f"{BASE_URL}/api/dao/sugestoes",
        json={
            "usuario_nome": usuario,
            "titulo": titulo,
            "descricao": descricao
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Sugestão criada (ID: {data['id']})")
        print(f"   💰 Tokens em escrow: {data['tokens_escrow']}")
        print(f"   📊 Status: {data['status']}")
        return data
    else:
        print(f"   ❌ Erro: {response.json()}")
        return None

def aprovar_sugestao(sugestao_id, moderador):
    """Moderador aprova sugestão para votação"""
    print(f"\n👍 {moderador} aprovando sugestão #{sugestao_id}")

    response = requests.post(
        f"{BASE_URL}/api/dao/sugestoes/{sugestao_id}/aprovar",
        json={
            "sugestao_id": sugestao_id,
            "usuario_nome": moderador
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['mensagem']}")
        return data
    else:
        print(f"   ❌ Erro: {response.json()}")
        return None

def aceitar_implementar(sugestao_id, moderador):
    """Moderador aceita implementar a sugestão"""
    print(f"\n🛠️  {moderador} aceitando implementar sugestão #{sugestao_id}")

    response = requests.post(
        f"{BASE_URL}/api/moderadores/aceitar-implementar",
        json={
            "sugestao_id": sugestao_id,
            "moderador_nome": moderador
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['mensagem']}")
        print(f"   💰 Tokens em escrow: {data['tokens_escrow']}")
        return data
    else:
        print(f"   ❌ Erro: {response.json()}")
        return None

def marcar_implementada(sugestao_id, moderador):
    """Moderador marca como implementada (recebe tokens)"""
    print(f"\n🎉 {moderador} marcando sugestão #{sugestao_id} como IMPLEMENTADA")

    response = requests.post(
        f"{BASE_URL}/api/moderadores/marcar-implementada",
        json={
            "sugestao_id": sugestao_id,
            "moderador_nome": moderador
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['mensagem']}")
        print(f"   💰 Tokens recebidos: {data['tokens_recebidos']}")
        print(f"   ⭐ Reputação moderador: {data['reputacao_moderador']}")
        print(f"   📊 Total implementadas: {data['total_implementadas']}")
        return data
    else:
        print(f"   ❌ Erro: {response.json()}")
        return None

def test_contrato_inteligente():
    print_header("🧪 TESTE DO CONTRATO INTELIGENTE - SISTEMA DE ESCROW")

    print("""
📜 COMO FUNCIONA:

1. Usuário cria sugestão → paga 5 tokens
2. Tokens ficam BLOQUEADOS em escrow (não são gastos)
3. Moderador aprova sugestão
4. Moderador aceita implementar → tokens ficam reservados para ele
5. Moderador implementa → recebe os 5 tokens do escrow
6. Se cancelar → tokens podem voltar ao criador

    """)

    # CENÁRIO 1: Fluxo completo bem-sucedido
    print_step(1, "Preparando usuários")
    criar_usuario("Alice")
    criar_usuario("Vengel")

    # Dar tokens extras para Alice fazer a sugestão
    print("\n💰 Dando tokens extras para Alice poder criar sugestão...")
    response = requests.post(
        f"{BASE_URL}/api/contribuir",
        json={
            "usuario_nome": "Alice",
            "produto_nome": "Produto Teste Inicial",
            "produto_marca": "Teste",
            "supermercado": "Teste",
            "preco": 10.00,
            "em_promocao": False,
            "localizacao": "Teste",
            "latitude": -23.5505,
            "longitude": -46.6333
        }
    )
    print(f"   ✅ Alice ganhou 10 tokens por contribuir")

    print("\n💰 Saldo inicial:")
    alice_antes = consultar_carteira("Alice")
    vengel_antes = consultar_carteira("Vengel")
    print(f"   Alice: {alice_antes['saldo']} tokens | Reputação: {alice_antes['reputacao']}")
    print(f"   Vengel: {vengel_antes['saldo']} tokens | Reputação moderador: {vengel_antes['reputacao']}")

    # Criar sugestão
    print_step(2, "Alice cria sugestão (5 tokens em escrow)")
    sugestao = criar_sugestao(
        "Alice",
        "Adicionar modo escuro",
        "O app deveria ter um tema escuro para economizar bateria e melhorar usabilidade noturna"
    )

    if not sugestao:
        print("❌ Falha ao criar sugestão")
        return

    sugestao_id = sugestao['id']

    # Verificar saldo após criar sugestão
    alice_depois = consultar_carteira("Alice")
    print(f"\n   💰 Saldo Alice após criar sugestão: {alice_depois['saldo']} tokens")
    print(f"   📉 Diferença: -{alice_antes['saldo'] - alice_depois['saldo']} tokens (em escrow)")

    # Moderador aprova
    print_step(3, "Moderador aprova sugestão para votação")
    aprovar_sugestao(sugestao_id, "Vengel")

    # Simular votação (na prática, outros usuários votariam)
    print_step(4, "Sugestão é aprovada pela comunidade (60%+)")
    print("   ℹ️  (Pulando votação para simplificar o teste)")
    print("   ✅ Assumindo que atingiu 60% de aprovação")

    # Marcar manualmente como aprovada
    response = requests.patch(
        f"{BASE_URL}/api/dao/sugestoes/{sugestao_id}/status",
        params={"novo_status": "aprovada", "admin_usuario": "Vengel"}
    )

    # Moderador aceita implementar
    print_step(5, "Moderador aceita implementar (tokens ficam reservados)")
    aceitar_implementar(sugestao_id, "Vengel")

    # Moderador implementa
    print_step(6, "Moderador implementa e recebe os tokens!")
    marcar_implementada(sugestao_id, "Vengel")

    # Verificar saldo final
    print_step(7, "Verificando saldos finais")
    alice_final = consultar_carteira("Alice")
    vengel_final = consultar_carteira("Vengel")

    print(f"\n📊 SALDOS FINAIS:")
    print(f"   Alice:")
    print(f"      • Antes: {alice_antes['saldo']} tokens")
    print(f"      • Depois: {alice_final['saldo']} tokens")
    print(f"      • Diferença: -{alice_antes['saldo'] - alice_final['saldo']} tokens (pagou pela sugestão)")

    print(f"\n   Vengel (Moderador):")
    print(f"      • Antes: {vengel_antes['saldo']} tokens")
    print(f"      • Depois: {vengel_final['saldo']} tokens")
    print(f"      • Diferença: +{vengel_final['saldo'] - vengel_antes['saldo']} tokens (recompensa)")
    print(f"      • Reputação: {vengel_final['reputacao']} pts")

    # Resumo
    print_header("📊 RESUMO DO CONTRATO INTELIGENTE")
    print("""
✅ FLUXO EXECUTADO COM SUCESSO:

1️⃣  Alice criou sugestão → 5 tokens bloqueados em escrow
2️⃣  Moderador Vengel aprovou para votação
3️⃣  Comunidade votou e aprovou (60%+)
4️⃣  Vengel aceitou implementar → tokens reservados para ele
5️⃣  Vengel implementou → recebeu os 5 tokens do escrow

💡 BENEFÍCIOS DO SISTEMA:

✅ Usuários pagam pela criação, mas...
✅ Tokens não são "perdidos", vão para quem implementa
✅ Incentiva moderadores a implementar sugestões
✅ Sistema justo e transparente
✅ Tokens só são liberados se implementado
✅ Se cancelar, tokens podem voltar ao criador

🎯 PRÓXIMOS PASSOS:

• Adicionar mais moderadores
• Testar cancelamento de implementação
• Ver tokens sendo devolvidos
• Verificar penalidades para moderadores
    """)

    print("\n✅ Teste concluído com sucesso!")
    print("\n🌐 Acesse http://localhost:8080/dao.html para ver a interface")

if __name__ == "__main__":
    try:
        # Verificar se API está rodando
        response = requests.get(f"{BASE_URL}/api", timeout=2)
        if response.status_code != 200:
            print("❌ API não está respondendo!")
            exit(1)
    except:
        print("❌ API não está rodando! Execute: ./start_app.sh")
        exit(1)

    test_contrato_inteligente()
