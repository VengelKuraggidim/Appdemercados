#!/usr/bin/env python3
"""
Teste do sistema de validação automática com produto novo
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def testar_validacao_produto_novo():
    print("🧪 TESTANDO SISTEMA DE VALIDAÇÃO AUTOMÁTICA (PRODUTO NOVO)\n")

    # Usar um produto novo que não existe no banco
    produto_nome = f"Feijão Preto Teste {int(time.time())}"

    # Cenário de teste:
    # 1. Alice adiciona por R$ 8,00 (primeiro preço - sem validação)
    # 2. Bob adiciona por R$ 8,20 (segundo preço - sem validação, precisa de 2+)
    # 3. Carol adiciona por R$ 7,80 (terceiro preço - agora valida! Mediana ~8,00, muito próximo)
    # 4. David adiciona por R$ 15,00 (quarto preço - outlier! 87.5% acima da mediana)

    cenarios = [
        ("Alice", 8.00, "Primeiro preço - sem validação ainda"),
        ("Bob", 8.20, "Segundo preço - sem validação ainda"),
        ("Carol", 7.80, "Terceiro preço - agora valida! ✅"),
        ("David", 15.00, "Outlier - muito acima! ⚠️")
    ]

    print(f"📊 CENÁRIO DE TESTE - {produto_nome}")
    for usuario, preco, descricao in cenarios:
        print(f"• {usuario}: R$ {preco:.2f} - {descricao}")
    print()

    print("-" * 60)

    for i, (usuario, preco, descricao) in enumerate(cenarios, 1):
        print(f"\n{i}. {usuario} adicionando R$ {preco:.2f}...")

        contribuicao = {
            "usuario_nome": usuario,
            "produto_nome": produto_nome,
            "produto_marca": "Teste",
            "supermercado": "Supermercado Teste",
            "preco": preco,
            "em_promocao": False,
            "localizacao": "Teste",
            "latitude": -23.5505,
            "longitude": -46.6333
        }

        response = requests.post(
            f"{BASE_URL}/api/contribuir",
            json=contribuicao
        )

        if response.status_code == 200:
            resultado = response.json()

            # Mostrar tokens
            if "recompensa" in resultado:
                recomp = resultado["recompensa"]
                print(f"   💰 Tokens: +{recomp.get('tokens_ganhos', 0)} (Total: {recomp.get('saldo_atual', 0)})")

            # Mostrar validação
            if "validacao" in resultado:
                validacao = resultado["validacao"]
                if validacao.get("sucesso"):
                    alteracao = validacao.get("alteracao_reputacao", 0)
                    mensagem = validacao.get("mensagem", "")

                    if "Poucos preços" in mensagem:
                        print(f"   ⏳ Validação: aguardando mais preços para comparar")
                    elif alteracao > 0:
                        diferenca = validacao.get("diferenca_percentual", 0)
                        mediana = validacao.get("mediana", 0)
                        print(f"   ✅ Validação: +{alteracao} pts")
                        print(f"      Preço {diferenca:.1f}% diferente da mediana (R$ {mediana:.2f})")
                    elif alteracao < 0:
                        diferenca = validacao.get("diferenca_percentual", 0)
                        mediana = validacao.get("mediana", 0)
                        print(f"   ⚠️  Validação: {alteracao} pts (PENALIDADE)")
                        print(f"      Preço {diferenca:.1f}% diferente da mediana (R$ {mediana:.2f})")
                    else:
                        diferenca = validacao.get("diferenca_percentual", 0)
                        print(f"   ℹ️  Validação: sem alteração (preço aceitável, {diferenca:.1f}% de diferença)")
        else:
            print(f"   ❌ Erro: {response.status_code}")

    print("\n" + "=" * 60)
    print("\n📈 REPUTAÇÃO FINAL DOS USUÁRIOS:\n")

    for usuario, _, _ in cenarios:
        response = requests.get(f"{BASE_URL}/api/carteira/{usuario}")
        if response.status_code == 200:
            carteira = response.json()
            reputacao = carteira.get("reputacao", 100)
            saldo = carteira.get("saldo", 0)

            # Calcular variação
            variacao = reputacao - 100
            if variacao > 0:
                status = f"✅ +{variacao}"
            elif variacao < 0:
                status = f"⚠️  {variacao}"
            else:
                status = "➖  0"

            print(f"{usuario:10} → Reputação: {reputacao:3} pts ({status}) | Saldo: {saldo:.1f} tokens")
        else:
            print(f"{usuario:10} → Erro ao consultar")

    print("\n✅ Teste concluído!")
    print("\n📊 RESUMO DO COMPORTAMENTO:")
    print("1. Primeiros 2 preços: sem validação (precisa de pelo menos 2 preços para comparar)")
    print("2. Preços próximos da mediana (±30%): ganham +2 reputação ✅")
    print("3. Preços muito diferentes (>50%): perdem -5 reputação ⚠️")
    print("4. Preços aceitáveis (30-50%): sem alteração ℹ️")

if __name__ == "__main__":
    testar_validacao_produto_novo()
