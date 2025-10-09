#!/usr/bin/env python3
"""
Teste completo do sistema de votação da DAO
Testa aprovação automática e rejeição automática
"""

import requests
import time
from datetime import datetime

API_URL = 'http://localhost:8000/api'

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

# Lista de usuários para teste
USUARIOS = ['Alice', 'Bob', 'Carol', 'Dave', 'Eve']

def criar_usuarios():
    """Cria carteiras para todos os usuários"""
    print_header("CRIANDO USUÁRIOS")
    for usuario in USUARIOS:
        try:
            response = requests.post(f"{API_URL}/carteira/criar", json={
                "usuario_nome": usuario,
                "senha": "senha123"
            })
            if response.status_code == 200:
                print_success(f"Carteira criada para {usuario}")
            else:
                print_info(f"Carteira de {usuario} já existe")
        except Exception as e:
            print_error(f"Erro ao criar carteira de {usuario}: {e}")

def dar_tokens_usuarios():
    """Dá tokens a todos os usuários através de contribuições"""
    print_header("DANDO TOKENS AOS USUÁRIOS")
    for usuario in USUARIOS:
        try:
            # Fazer 2 contribuições para cada usuário (20 tokens total)
            for i in range(2):
                response = requests.post(f"{API_URL}/contribuir", json={
                    "usuario_nome": usuario,
                    "produto_nome": f"Produto Teste {usuario} {i}",
                    "produto_marca": "Marca Teste",
                    "supermercado": f"Loja Teste {i}",
                    "preco": 10.0 + i,
                    "em_promocao": False,
                    "localizacao": "São Paulo",
                    "latitude": -23.5505,
                    "longitude": -46.6333
                })
                if response.status_code == 200:
                    data = response.json()
                    tokens_ganhos = data.get('tokens_ganhos', 10)
                    print_success(f"{usuario} contribuiu e ganhou {tokens_ganhos} tokens")
                else:
                    print_warning(f"{usuario} erro na contribuição {i}: {response.status_code} - {response.text}")
                time.sleep(0.2)

            # Verificar saldo
            response = requests.get(f"{API_URL}/carteira/{usuario}")
            if response.status_code == 200:
                saldo = response.json()['saldo']
                print_info(f"Saldo de {usuario}: {saldo} tokens")
        except Exception as e:
            print_error(f"Erro ao dar tokens a {usuario}: {e}")

def criar_sugestao(usuario, titulo, descricao):
    """Cria uma sugestão"""
    try:
        response = requests.post(f"{API_URL}/dao/sugestoes", json={
            "usuario_nome": usuario,
            "titulo": titulo,
            "descricao": descricao
        })
        if response.status_code == 200:
            data = response.json()
            # Tentar pegar o ID da sugestão de diferentes formas
            if 'sugestao' in data and 'id' in data['sugestao']:
                sugestao_id = data['sugestao']['id']
            elif 'id' in data:
                sugestao_id = data['id']
            else:
                print_error(f"Resposta inesperada: {data}")
                return None
            print_success(f"Sugestão #{sugestao_id} criada por {usuario}: '{titulo}'")
            return sugestao_id
        else:
            print_error(f"Erro ao criar sugestão ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print_error(f"Erro ao criar sugestão: {e}")
        import traceback
        traceback.print_exc()
        return None

def aprovar_sugestao(sugestao_id):
    """Aprova uma sugestão como moderador"""
    try:
        response = requests.post(f"{API_URL}/dao/sugestoes/{sugestao_id}/aprovar", json={
            "sugestao_id": sugestao_id,
            "usuario_nome": "Vengel"
        })
        if response.status_code == 200:
            print_success(f"Sugestão #{sugestao_id} aprovada para votação")
            return True
        else:
            print_error(f"Erro ao aprovar sugestão ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro ao aprovar sugestão: {e}")
        return False

def votar(usuario, sugestao_id, a_favor, tokens=1):
    """Vota em uma sugestão"""
    try:
        response = requests.post(f"{API_URL}/dao/votar", json={
            "sugestao_id": sugestao_id,
            "usuario_nome": usuario,
            "voto_favor": a_favor,  # Usar voto_favor em vez de a_favor
            "tokens_usados": tokens
        })
        if response.status_code == 200:
            voto_tipo = "👍 a favor" if a_favor else "👎 contra"
            print_success(f"{usuario} votou {voto_tipo} na sugestão #{sugestao_id} ({tokens} token(s))")
            return True
        else:
            try:
                error_msg = response.json().get('detail', response.text)
            except:
                error_msg = response.text
            print_warning(f"{usuario} não conseguiu votar ({response.status_code}): {error_msg}")
            return False
    except Exception as e:
        print_error(f"Erro ao votar: {e}")
        return False

def verificar_sugestao(sugestao_id):
    """Verifica o status de uma sugestão"""
    try:
        response = requests.get(f"{API_URL}/dao/sugestoes")
        if response.status_code == 200:
            sugestoes = response.json()
            sugestao = next((s for s in sugestoes if s['id'] == sugestao_id), None)
            if sugestao:
                status = sugestao['status']
                aprovacao = sugestao['porcentagem_aprovacao']
                favor = sugestao['total_votos_favor']
                contra = sugestao['total_votos_contra']

                print_info(f"Sugestão #{sugestao_id}: {status}")
                print_info(f"  Votos: {favor} a favor, {contra} contra ({aprovacao:.1f}% aprovação)")

                return sugestao
            else:
                print_warning(f"Sugestão #{sugestao_id} não encontrada")
                return None
    except Exception as e:
        print_error(f"Erro ao verificar sugestão: {e}")
        return None

def main():
    print_header("🧪 TESTE COMPLETO DO SISTEMA DE VOTAÇÃO DA DAO")

    # 1. Criar usuários
    criar_usuarios()
    time.sleep(1)

    # 2. Dar tokens aos usuários
    dar_tokens_usuarios()
    time.sleep(1)

    # 3. Criar sugestões
    print_header("CRIANDO SUGESTÕES")

    sugestao_aprovada = criar_sugestao(
        'Alice',
        'IMPLEMENTAR MODO ESCURO',
        'Adicionar tema escuro para melhorar a experiência à noite'
    )
    time.sleep(0.5)

    sugestao_rejeitada = criar_sugestao(
        'Bob',
        'Remover funcionalidade de preços',
        'Essa funcionalidade não faz sentido para o app'
    )
    time.sleep(0.5)

    sugestao_intermediaria = criar_sugestao(
        'Carol',
        'Adicionar notificações push',
        'Notificar usuários sobre novos preços'
    )
    time.sleep(1)

    if not all([sugestao_aprovada, sugestao_rejeitada, sugestao_intermediaria]):
        print_error("Erro ao criar sugestões. Abortando teste.")
        return

    # 4. Aprovar todas as sugestões para votação
    print_header("APROVANDO SUGESTÕES PARA VOTAÇÃO (como moderador)")
    aprovar_sugestao(sugestao_aprovada)
    time.sleep(0.5)
    aprovar_sugestao(sugestao_rejeitada)
    time.sleep(0.5)
    aprovar_sugestao(sugestao_intermediaria)
    time.sleep(1)

    # 5. TESTE 1: Sugestão com maioria a favor (deve ser APROVADA automaticamente)
    print_header("TESTE 1: Sugestão com 100% de votos a favor")
    print_info(f"Votando na sugestão #{sugestao_aprovada}: '{verificar_sugestao(sugestao_aprovada)['titulo']}'")

    # Bob, Carol, Dave e Eve votam a favor (Alice criou, não pode votar)
    votar('Bob', sugestao_aprovada, a_favor=True, tokens=4)  # 2 votos (quadrático)
    time.sleep(0.5)
    votar('Carol', sugestao_aprovada, a_favor=True, tokens=1)
    time.sleep(0.5)
    votar('Dave', sugestao_aprovada, a_favor=True, tokens=1)
    time.sleep(0.5)
    votar('Eve', sugestao_aprovada, a_favor=True, tokens=1)
    time.sleep(1)

    resultado1 = verificar_sugestao(sugestao_aprovada)
    if resultado1 and resultado1['status'] == 'aprovada':
        print_success("✅ TESTE 1 PASSOU: Sugestão aprovada automaticamente com >60% de votos a favor")
    else:
        print_error(f"❌ TESTE 1 FALHOU: Esperado 'aprovada', obtido '{resultado1['status']}'")

    time.sleep(1)

    # 6. TESTE 2: Sugestão com maioria contra (deve ser REJEITADA automaticamente)
    print_header("TESTE 2: Sugestão com 100% de votos contra")
    print_info(f"Votando na sugestão #{sugestao_rejeitada}: '{verificar_sugestao(sugestao_rejeitada)['titulo']}'")

    # Alice, Carol, Dave e Eve votam contra (Bob criou, não pode votar)
    votar('Alice', sugestao_rejeitada, a_favor=False, tokens=4)  # 2 votos contra
    time.sleep(0.5)
    votar('Carol', sugestao_rejeitada, a_favor=False, tokens=1)
    time.sleep(0.5)
    votar('Dave', sugestao_rejeitada, a_favor=False, tokens=1)
    time.sleep(0.5)
    votar('Eve', sugestao_rejeitada, a_favor=False, tokens=1)
    time.sleep(1)

    resultado2 = verificar_sugestao(sugestao_rejeitada)
    if resultado2 and resultado2['status'] == 'rejeitada':
        print_success("✅ TESTE 2 PASSOU: Sugestão rejeitada automaticamente com <40% de aprovação")
    else:
        print_error(f"❌ TESTE 2 FALHOU: Esperado 'rejeitada', obtido '{resultado2['status']}'")

    time.sleep(1)

    # 7. TESTE 3: Sugestão com votos mistos (deve continuar EM VOTAÇÃO)
    print_header("TESTE 3: Sugestão com votos mistos (50%)")
    print_info(f"Votando na sugestão #{sugestao_intermediaria}: '{verificar_sugestao(sugestao_intermediaria)['titulo']}'")

    # Alice e Bob votam a favor, Dave e Eve votam contra (Carol criou)
    votar('Alice', sugestao_intermediaria, a_favor=True, tokens=1)
    time.sleep(0.5)
    votar('Bob', sugestao_intermediaria, a_favor=True, tokens=1)
    time.sleep(0.5)
    votar('Dave', sugestao_intermediaria, a_favor=False, tokens=1)
    time.sleep(0.5)
    votar('Eve', sugestao_intermediaria, a_favor=False, tokens=1)
    time.sleep(1)

    resultado3 = verificar_sugestao(sugestao_intermediaria)
    if resultado3 and resultado3['status'] == 'em_votacao':
        print_success("✅ TESTE 3 PASSOU: Sugestão continua em votação (entre 40-60%)")
    else:
        print_error(f"❌ TESTE 3 FALHOU: Esperado 'em_votacao', obtido '{resultado3['status']}'")

    # 8. Relatório final
    print_header("RELATÓRIO FINAL")
    print_info("Verificando todas as sugestões:")
    verificar_sugestao(sugestao_aprovada)
    verificar_sugestao(sugestao_rejeitada)
    verificar_sugestao(sugestao_intermediaria)

    print_header("🎉 TESTES CONCLUÍDOS!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nTeste interrompido pelo usuário")
    except Exception as e:
        print_error(f"Erro durante o teste: {e}")
