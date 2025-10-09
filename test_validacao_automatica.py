#!/usr/bin/env python3
"""
Teste do sistema de validação automática de preços
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def testar_validacao_automatica():
    print("🧪 TESTANDO SISTEMA DE VALIDAÇÃO AUTOMÁTICA\n")

    # Cenário de teste:
    # 1. Usuário A adiciona Arroz Tio João por R$ 10,00
    # 2. Usuário B adiciona Arroz Tio João por R$ 10,50
    # 3. Usuário C adiciona Arroz Tio João por R$ 9,80
    # 4. Usuário D adiciona Arroz Tio João por R$ 25,00 (outlier - muito diferente!)

    usuarios = ["UserA", "UserB", "UserC", "UserD"]
    precos = [10.00, 10.50, 9.80, 25.00]

    print("📊 CENÁRIO DE TESTE:")
    print(f"• Produto: Arroz Tio João 5kg")
    print(f"• UserA: R$ 10,00")
    print(f"• UserB: R$ 10,50")
    print(f"• UserC: R$ 9,80")
    print(f"• UserD: R$ 25,00 (OUTLIER - muito acima da média)\n")

    print("-" * 60)

    for i, (usuario, preco) in enumerate(zip(usuarios, precos), 1):
        print(f"\n{i}. {usuario} adicionando preço R$ {preco:.2f}...")

        contribuicao = {
            "usuario_nome": usuario,
            "produto_nome": "Arroz Tio João 5kg",
            "produto_marca": "Tio João",
            "supermercado": "Supermercado Teste",
            "preco": preco,
            "em_promocao": False,
            "localizacao": "Teste",
            "latitude": -23.5505,
            "longitude": -46.6333
        }

        # Adicionar contribuição
        response = requests.post(
            f"{BASE_URL}/api/contribuir",
            json=contribuicao
        )

        if response.status_code == 200:
            resultado = response.json()

            # Mostrar resultado da recompensa
            if "recompensa" in resultado:
                recomp = resultado["recompensa"]
                print(f"   💰 Tokens: {recomp.get('tokens_ganhos', 0)} (Saldo: {recomp.get('saldo_atual', 0)})")

            # Mostrar resultado da validação automática
            if "validacao" in resultado:
                validacao = resultado["validacao"]
                if validacao.get("sucesso"):
                    alteracao = validacao.get("alteracao_reputacao", 0)
                    diferenca = validacao.get("diferenca_percentual", 0)
                    mediana = validacao.get("mediana", 0)

                    if alteracao > 0:
                        print(f"   ✅ Reputação: +{alteracao} pts (preço {diferenca:.1f}% diferente da mediana R$ {mediana:.2f})")
                    elif alteracao < 0:
                        print(f"   ⚠️  Reputação: {alteracao} pts (preço {diferenca:.1f}% diferente da mediana R$ {mediana:.2f})")
                    else:
                        if "Poucos preços" in validacao.get("mensagem", ""):
                            print(f"   ℹ️  Sem validação (poucos preços para comparar)")
                        else:
                            print(f"   ℹ️  Reputação: sem alteração (preço {diferenca:.1f}% diferente da mediana)")

                    print(f"   📝 {validacao.get('mensagem', '')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   {response.text}")

    print("\n" + "=" * 60)
    print("\n📈 CONSULTANDO REPUTAÇÃO FINAL DOS USUÁRIOS:\n")

    for usuario in usuarios:
        response = requests.get(f"{BASE_URL}/api/carteira/{usuario}")
        if response.status_code == 200:
            carteira = response.json()
            reputacao = carteira.get("reputacao", 100)
            saldo = carteira.get("saldo", 0)
            print(f"{usuario:10} → Reputação: {reputacao:3} pts | Saldo: {saldo:.1f} tokens")
        else:
            print(f"{usuario:10} → Erro ao consultar carteira")

    print("\n✅ Teste concluído!")
    print("\nℹ️  INTERPRETAÇÃO DOS RESULTADOS:")
    print("• UserA, UserB, UserC: preços próximos → devem ter +2 reputação")
    print("• UserD: preço muito diferente (outlier) → deve ter -5 reputação")

if __name__ == "__main__":
    testar_validacao_automatica()
