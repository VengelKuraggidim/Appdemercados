#!/usr/bin/env python3
"""
Script de teste completo para validação automática no frontend
Simula o comportamento real dos usuários adicionando preços
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(texto):
    print("\n" + "="*70)
    print(f"  {texto}")
    print("="*70 + "\n")

def print_step(numero, texto):
    print(f"\n📌 PASSO {numero}: {texto}")
    print("-" * 70)

def consultar_carteira(usuario):
    """Consulta informações da carteira"""
    response = requests.get(f"{BASE_URL}/api/carteira/{usuario}")
    if response.status_code == 200:
        return response.json()
    return None

def criar_usuario(nome):
    """Cria ou obtém carteira do usuário"""
    print(f"👤 Criando usuário: {nome}")
    response = requests.post(
        f"{BASE_URL}/api/carteira/criar",
        json={"usuario_nome": nome}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Usuário criado - Saldo: {data['saldo']} tokens")
        # Buscar reputação
        carteira = consultar_carteira(nome)
        if carteira:
            print(f"   📊 Reputação: {carteira.get('reputacao', 100)} pts")
        return data
    else:
        print(f"   ⚠️  Usuário já existe ou erro: {response.text[:100]}")
        return None

def adicionar_preco(usuario, produto, preco_valor):
    """Adiciona um preço e mostra resultado da validação"""
    print(f"\n💰 {usuario} adicionando {produto} por R$ {preco_valor:.2f}...")

    contribuicao = {
        "usuario_nome": usuario,
        "produto_nome": produto,
        "produto_marca": "Marca Teste",
        "supermercado": "Supermercado Teste",
        "preco": preco_valor,
        "em_promocao": False,
        "localizacao": "São Paulo - SP",
        "latitude": -23.5505,
        "longitude": -46.6333
    }

    response = requests.post(
        f"{BASE_URL}/api/contribuir",
        json=contribuicao
    )

    if response.status_code == 200:
        data = response.json()

        # Mostrar recompensa de tokens
        if "recompensa" in data:
            recomp = data["recompensa"]
            print(f"   💎 +{recomp.get('tokens_ganhos', 0)} tokens (Saldo: {recomp.get('saldo_atual', 0)})")

        # Mostrar resultado da validação automática
        if "validacao" in data:
            val = data["validacao"]
            alteracao = val.get("alteracao_reputacao", 0)
            mensagem = val.get("mensagem", "")

            if alteracao > 0:
                print(f"   ✅ VALIDAÇÃO: +{alteracao} reputação")
                print(f"      {mensagem}")
                if "diferenca_percentual" in val:
                    print(f"      📊 Diferença da mediana: {val['diferenca_percentual']:.1f}%")
                    print(f"      📈 Mediana atual: R$ {val.get('mediana', 0):.2f}")
            elif alteracao < 0:
                print(f"   ⚠️  VALIDAÇÃO: {alteracao} reputação (PENALIDADE)")
                print(f"      {mensagem}")
                if "diferenca_percentual" in val:
                    print(f"      📊 Diferença da mediana: {val['diferenca_percentual']:.1f}%")
                    print(f"      📈 Mediana atual: R$ {val.get('mediana', 0):.2f}")
            else:
                if "Poucos preços" in mensagem:
                    print(f"   ⏳ VALIDAÇÃO: Aguardando mais preços para comparar")
                else:
                    print(f"   ℹ️  VALIDAÇÃO: Sem alteração de reputação")
                    print(f"      {mensagem}")

        return data
    else:
        print(f"   ❌ Erro: {response.status_code}")
        print(f"   {response.text[:200]}")
        return None

def test_validacao_automatica():
    print_header("🧪 TESTE DE VALIDAÇÃO AUTOMÁTICA NO FRONTEND")

    # Produto de teste único
    produto = f"Café Premium Teste {int(time.time())}"
    print(f"📦 Produto de teste: {produto}\n")

    # Cenário de teste
    cenarios = [
        ("Alice", 18.00, "Primeiro preço - sem validação"),
        ("Bob", 18.50, "Segundo preço - sem validação"),
        ("Carol", 17.80, "Terceiro preço - VALIDA! (próximo da mediana)"),
        ("David", 35.00, "Quarto preço - OUTLIER! (muito diferente)")
    ]

    print("📋 CENÁRIO DE TESTE:")
    for usuario, preco, desc in cenarios:
        print(f"   • {usuario}: R$ {preco:.2f} - {desc}")

    # Criar usuários
    print_step(1, "Criando usuários")
    for usuario, _, _ in cenarios:
        criar_usuario(usuario)
        time.sleep(0.3)

    # Adicionar preços
    print_step(2, "Adicionando preços e validando automaticamente")
    for i, (usuario, preco, desc) in enumerate(cenarios, 1):
        print(f"\n[{i}/{len(cenarios)}]", end=" ")
        adicionar_preco(usuario, produto, preco)
        time.sleep(0.5)

    # Consultar reputações finais
    print_step(3, "Consultando reputações finais")
    print(f"\n{'Usuário':<12} {'Reputação':<12} {'Variação':<15} {'Saldo Tokens':<15}")
    print("-" * 70)

    for usuario, _, _ in cenarios:
        carteira = consultar_carteira(usuario)
        if carteira:
            reputacao = carteira.get("reputacao", 100)
            saldo = carteira.get("saldo", 0)
            variacao = reputacao - 100

            if variacao > 0:
                status = f"✅ +{variacao}"
                cor = "verde"
            elif variacao < 0:
                status = f"⚠️  {variacao}"
                cor = "vermelho"
            else:
                status = "➖  0"
                cor = "neutro"

            print(f"{usuario:<12} {reputacao:<12.0f} {status:<15} {saldo:<15.0f}")

    # Resumo
    print_header("📊 RESUMO DO TESTE")
    print("""
✅ COMPORTAMENTO ESPERADO:

1️⃣  Alice e Bob (primeiros 2 preços):
   → Sem validação automática (precisa de 2+ preços para comparar)
   → Reputação: 100 pts (sem mudança)

2️⃣  Carol (terceiro preço próximo da mediana):
   → ✅ Validação positiva: +2 reputação
   → Reputação: 102 pts

3️⃣  David (outlier - muito diferente):
   → ⚠️  Penalidade: -5 reputação
   → Reputação: 95 pts

💡 O sistema compara cada novo preço com a mediana dos preços existentes:
   • ±30% da mediana: +2 reputação ✅
   • 30-50% de diferença: sem alteração ℹ️
   • >50% de diferença: -5 reputação ⚠️
    """)

    print("\n✅ Teste concluído!")
    print("\n🌐 Você pode ver os resultados no frontend em:")
    print("   • http://localhost:8080")
    print("   • Faça login com qualquer usuário acima")
    print("   • Clique em 'Minha Carteira' para ver reputação e histórico")

if __name__ == "__main__":
    try:
        # Verificar se API está rodando
        response = requests.get(f"{BASE_URL}/api", timeout=2)
        if response.status_code != 200:
            print("❌ API não está respondendo corretamente!")
            exit(1)
    except requests.exceptions.RequestException as e:
        print("❌ Erro: API não está rodando!")
        print(f"   Certifique-se de que o servidor está ativo em {BASE_URL}")
        print(f"\n   Execute: ./start_app.sh")
        exit(1)

    test_validacao_automatica()
