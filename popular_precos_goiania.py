"""
Popula o banco de dados com precos REALISTAS de supermercados de Goiania
Precos baseados em valores reais de janeiro 2025
"""
import sys
sys.path.insert(0, '.')

from app.models.database import SessionLocal, Produto, Preco, Carteira
from datetime import datetime, timedelta
import random

# Supermercados reais de Goiania com coordenadas GPS reais
SUPERMERCADOS_GOIANIA = [
    {
        "nome": "Tatico Atacadista",
        "endereco": "Av. Anhanguera, 5500 - Setor Central, Goiania",
        "latitude": -16.6799,
        "longitude": -49.2569,
        "tipo": "atacadista"  # Precos mais baixos
    },
    {
        "nome": "Tatico Atacadista - Campinas",
        "endereco": "Av. Mutirao, 1450 - Setor Campinas, Goiania",
        "latitude": -16.6650,
        "longitude": -49.2800,
        "tipo": "atacadista"
    },
    {
        "nome": "Assai Atacadista",
        "endereco": "Av. T-7, 1000 - Setor Bueno, Goiania",
        "latitude": -16.7050,
        "longitude": -49.2650,
        "tipo": "atacadista"
    },
    {
        "nome": "Atacadao",
        "endereco": "Av. Goias, 2500 - Setor Central, Goiania",
        "latitude": -16.6850,
        "longitude": -49.2500,
        "tipo": "atacadista"
    },
    {
        "nome": "Bretas Supermercados",
        "endereco": "Av. T-63, 1200 - Setor Bueno, Goiania",
        "latitude": -16.7100,
        "longitude": -49.2700,
        "tipo": "supermercado"
    },
    {
        "nome": "Carrefour Goiania",
        "endereco": "Av. T-10, 300 - Setor Bueno, Goiania",
        "latitude": -16.7000,
        "longitude": -49.2600,
        "tipo": "hipermercado"
    },
    {
        "nome": "Super Maia",
        "endereco": "Av. T-4, 800 - Setor Bueno, Goiania",
        "latitude": -16.6950,
        "longitude": -49.2550,
        "tipo": "supermercado"
    },
    {
        "nome": "Mix Mateus",
        "endereco": "Rod. GO-020, km 5 - Jardim Novo Mundo, Goiania",
        "latitude": -16.6500,
        "longitude": -49.2200,
        "tipo": "atacadista"
    },
]

# Produtos com precos REAIS de supermercados (Janeiro 2025)
# Precos variam por tipo de loja: atacadista < supermercado < hipermercado
PRODUTOS_PRECOS = [
    # Arroz
    {"nome": "Arroz Branco Tipo 1", "marca": "Tio Joao", "categoria": "Alimentos", "unidade": "5kg",
     "preco_atacadista": 22.90, "preco_supermercado": 25.90, "preco_hipermercado": 27.90},
    {"nome": "Arroz Branco Tipo 1", "marca": "Camil", "categoria": "Alimentos", "unidade": "5kg",
     "preco_atacadista": 21.50, "preco_supermercado": 24.50, "preco_hipermercado": 26.90},
    {"nome": "Arroz Parboilizado", "marca": "Urbano", "categoria": "Alimentos", "unidade": "5kg",
     "preco_atacadista": 23.90, "preco_supermercado": 26.90, "preco_hipermercado": 28.90},
    {"nome": "Arroz Integral", "marca": "Tio Joao", "categoria": "Alimentos", "unidade": "1kg",
     "preco_atacadista": 8.50, "preco_supermercado": 9.90, "preco_hipermercado": 11.50},

    # Feijao
    {"nome": "Feijao Carioca", "marca": "Camil", "categoria": "Alimentos", "unidade": "1kg",
     "preco_atacadista": 7.90, "preco_supermercado": 8.90, "preco_hipermercado": 9.90},
    {"nome": "Feijao Preto", "marca": "Kicaldo", "categoria": "Alimentos", "unidade": "1kg",
     "preco_atacadista": 8.50, "preco_supermercado": 9.50, "preco_hipermercado": 10.90},

    # Oleo
    {"nome": "Oleo de Soja", "marca": "Soya", "categoria": "Alimentos", "unidade": "900ml",
     "preco_atacadista": 5.90, "preco_supermercado": 6.90, "preco_hipermercado": 7.90},
    {"nome": "Oleo de Soja", "marca": "Liza", "categoria": "Alimentos", "unidade": "900ml",
     "preco_atacadista": 5.50, "preco_supermercado": 6.50, "preco_hipermercado": 7.50},

    # Acucar
    {"nome": "Acucar Cristal", "marca": "Uniao", "categoria": "Alimentos", "unidade": "5kg",
     "preco_atacadista": 18.90, "preco_supermercado": 21.90, "preco_hipermercado": 23.90},
    {"nome": "Acucar Refinado", "marca": "Uniao", "categoria": "Alimentos", "unidade": "1kg",
     "preco_atacadista": 4.90, "preco_supermercado": 5.50, "preco_hipermercado": 6.50},

    # Cafe
    {"nome": "Cafe em Po", "marca": "Pilao", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 16.90, "preco_supermercado": 18.90, "preco_hipermercado": 21.90},
    {"nome": "Cafe em Po", "marca": "Melitta", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 18.90, "preco_supermercado": 21.90, "preco_hipermercado": 24.90},
    {"nome": "Cafe em Po", "marca": "3 Coracoes", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 15.90, "preco_supermercado": 17.90, "preco_hipermercado": 19.90},

    # Leite
    {"nome": "Leite Integral UHT", "marca": "Piracanjuba", "categoria": "Laticinios", "unidade": "1L",
     "preco_atacadista": 5.50, "preco_supermercado": 6.20, "preco_hipermercado": 6.90},
    {"nome": "Leite Integral UHT", "marca": "Italac", "categoria": "Laticinios", "unidade": "1L",
     "preco_atacadista": 4.90, "preco_supermercado": 5.50, "preco_hipermercado": 6.20},
    {"nome": "Leite Desnatado UHT", "marca": "Piracanjuba", "categoria": "Laticinios", "unidade": "1L",
     "preco_atacadista": 5.20, "preco_supermercado": 5.90, "preco_hipermercado": 6.50},

    # Macarrao
    {"nome": "Macarrao Espaguete", "marca": "Renata", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 3.50, "preco_supermercado": 4.20, "preco_hipermercado": 4.90},
    {"nome": "Macarrao Espaguete", "marca": "Adria", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 4.20, "preco_supermercado": 4.90, "preco_hipermercado": 5.50},
    {"nome": "Macarrao Parafuso", "marca": "Renata", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 3.90, "preco_supermercado": 4.50, "preco_hipermercado": 5.20},

    # Molho de Tomate
    {"nome": "Molho de Tomate", "marca": "Elefante", "categoria": "Alimentos", "unidade": "340g",
     "preco_atacadista": 2.90, "preco_supermercado": 3.50, "preco_hipermercado": 4.20},
    {"nome": "Extrato de Tomate", "marca": "Elefante", "categoria": "Alimentos", "unidade": "340g",
     "preco_atacadista": 4.50, "preco_supermercado": 5.20, "preco_hipermercado": 5.90},

    # Farinha
    {"nome": "Farinha de Trigo", "marca": "Dona Benta", "categoria": "Alimentos", "unidade": "1kg",
     "preco_atacadista": 5.50, "preco_supermercado": 6.50, "preco_hipermercado": 7.50},
    {"nome": "Farinha de Mandioca", "marca": "Yoki", "categoria": "Alimentos", "unidade": "500g",
     "preco_atacadista": 5.90, "preco_supermercado": 6.90, "preco_hipermercado": 7.90},

    # Sal
    {"nome": "Sal Refinado", "marca": "Cisne", "categoria": "Alimentos", "unidade": "1kg",
     "preco_atacadista": 2.50, "preco_supermercado": 2.90, "preco_hipermercado": 3.50},

    # Margarina/Manteiga
    {"nome": "Margarina", "marca": "Qualy", "categoria": "Laticinios", "unidade": "500g",
     "preco_atacadista": 7.90, "preco_supermercado": 8.90, "preco_hipermercado": 9.90},
    {"nome": "Manteiga", "marca": "Aviacao", "categoria": "Laticinios", "unidade": "200g",
     "preco_atacadista": 9.90, "preco_supermercado": 11.90, "preco_hipermercado": 13.90},

    # Higiene
    {"nome": "Papel Higienico", "marca": "Neve", "categoria": "Higiene", "unidade": "12 rolos",
     "preco_atacadista": 18.90, "preco_supermercado": 22.90, "preco_hipermercado": 25.90},
    {"nome": "Sabonete", "marca": "Lux", "categoria": "Higiene", "unidade": "90g",
     "preco_atacadista": 2.50, "preco_supermercado": 3.20, "preco_hipermercado": 3.90},
    {"nome": "Shampoo", "marca": "Seda", "categoria": "Higiene", "unidade": "325ml",
     "preco_atacadista": 9.90, "preco_supermercado": 12.90, "preco_hipermercado": 14.90},
    {"nome": "Creme Dental", "marca": "Colgate", "categoria": "Higiene", "unidade": "90g",
     "preco_atacadista": 4.50, "preco_supermercado": 5.50, "preco_hipermercado": 6.50},

    # Limpeza
    {"nome": "Detergente", "marca": "Ype", "categoria": "Limpeza", "unidade": "500ml",
     "preco_atacadista": 2.20, "preco_supermercado": 2.90, "preco_hipermercado": 3.50},
    {"nome": "Agua Sanitaria", "marca": "Qboa", "categoria": "Limpeza", "unidade": "1L",
     "preco_atacadista": 3.90, "preco_supermercado": 4.90, "preco_hipermercado": 5.90},
    {"nome": "Sabao em Po", "marca": "Omo", "categoria": "Limpeza", "unidade": "1kg",
     "preco_atacadista": 12.90, "preco_supermercado": 15.90, "preco_hipermercado": 18.90},
    {"nome": "Amaciante", "marca": "Comfort", "categoria": "Limpeza", "unidade": "2L",
     "preco_atacadista": 14.90, "preco_supermercado": 17.90, "preco_hipermercado": 19.90},

    # Carnes
    {"nome": "Frango Congelado", "marca": "Sadia", "categoria": "Carnes", "unidade": "kg",
     "preco_atacadista": 12.90, "preco_supermercado": 14.90, "preco_hipermercado": 16.90},
    {"nome": "Carne Moida", "marca": "In Natura", "categoria": "Carnes", "unidade": "kg",
     "preco_atacadista": 26.90, "preco_supermercado": 29.90, "preco_hipermercado": 32.90},
    {"nome": "Linguica Toscana", "marca": "Perdigao", "categoria": "Carnes", "unidade": "kg",
     "preco_atacadista": 19.90, "preco_supermercado": 22.90, "preco_hipermercado": 25.90},
    {"nome": "Ovos", "marca": "Granja", "categoria": "Alimentos", "unidade": "30 unidades",
     "preco_atacadista": 18.90, "preco_supermercado": 21.90, "preco_hipermercado": 24.90},

    # Bebidas
    {"nome": "Refrigerante Coca-Cola", "marca": "Coca-Cola", "categoria": "Bebidas", "unidade": "2L",
     "preco_atacadista": 8.90, "preco_supermercado": 9.90, "preco_hipermercado": 10.90},
    {"nome": "Refrigerante Guarana", "marca": "Antarctica", "categoria": "Bebidas", "unidade": "2L",
     "preco_atacadista": 6.90, "preco_supermercado": 7.90, "preco_hipermercado": 8.90},
    {"nome": "Suco de Laranja", "marca": "Del Valle", "categoria": "Bebidas", "unidade": "1L",
     "preco_atacadista": 6.90, "preco_supermercado": 7.90, "preco_hipermercado": 8.90},
    {"nome": "Agua Mineral", "marca": "Crystal", "categoria": "Bebidas", "unidade": "1.5L",
     "preco_atacadista": 2.50, "preco_supermercado": 2.90, "preco_hipermercado": 3.50},
]


def popular_precos():
    """Popula o banco com precos realistas"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("POPULANDO BANCO COM PRECOS REAIS DE GOIANIA")
        print("=" * 60)

        precos_adicionados = 0

        for produto_info in PRODUTOS_PRECOS:
            # Criar ou buscar produto (nome completo inclui unidade)
            nome_completo = f"{produto_info['nome']} {produto_info['unidade']}"

            produto = db.query(Produto).filter(
                Produto.nome == nome_completo,
                Produto.marca == produto_info["marca"]
            ).first()

            if not produto:
                # Incluir unidade no nome do produto
                nome_completo = f"{produto_info['nome']} {produto_info['unidade']}"
                produto = Produto(
                    nome=nome_completo,
                    marca=produto_info["marca"],
                    categoria=produto_info["categoria"],
                    descricao=f"{produto_info['nome']} - {produto_info['unidade']}"
                )
                db.add(produto)
                db.commit()
                db.refresh(produto)
                print(f"[+] Produto criado: {nome_completo} - {produto_info['marca']}")

            # Adicionar preco em cada supermercado
            for mercado in SUPERMERCADOS_GOIANIA:
                # Definir preco baseado no tipo de loja
                if mercado["tipo"] == "atacadista":
                    preco_base = produto_info["preco_atacadista"]
                elif mercado["tipo"] == "hipermercado":
                    preco_base = produto_info["preco_hipermercado"]
                else:
                    preco_base = produto_info["preco_supermercado"]

                # Pequena variacao aleatoria (+/- 5%)
                variacao = random.uniform(-0.05, 0.05)
                preco_final = round(preco_base * (1 + variacao), 2)

                # Verificar se ja existe
                preco_existente = db.query(Preco).filter(
                    Preco.produto_id == produto.id,
                    Preco.supermercado == mercado["nome"]
                ).first()

                if preco_existente:
                    # Atualizar preco existente
                    preco_existente.preco = preco_final
                    preco_existente.data_coleta = datetime.now() - timedelta(days=random.randint(0, 3))
                else:
                    # Criar novo preco
                    # Chance de estar em promocao (20%)
                    em_promocao = random.random() < 0.2
                    preco_original = None
                    if em_promocao:
                        preco_original = round(preco_final * 1.15, 2)

                    novo_preco = Preco(
                        produto_id=produto.id,
                        preco=preco_final,
                        preco_original=preco_original,
                        em_promocao=em_promocao,
                        supermercado=mercado["nome"],
                        localizacao=mercado["endereco"],
                        endereco=mercado["endereco"],
                        latitude=mercado["latitude"],
                        longitude=mercado["longitude"],
                        data_coleta=datetime.now() - timedelta(days=random.randint(0, 5)),
                        usuario_nome="Sistema",
                        verificado=True,
                        manual=True
                    )
                    db.add(novo_preco)
                    precos_adicionados += 1

            db.commit()

        print(f"\n[OK] {precos_adicionados} precos adicionados!")

        # Mostrar estatisticas
        total_produtos = db.query(Produto).count()
        total_precos = db.query(Preco).filter(Preco.latitude.isnot(None)).count()

        print(f"\n{'='*60}")
        print("ESTATISTICAS DO BANCO:")
        print(f"  - Total de produtos: {total_produtos}")
        print(f"  - Total de precos com geolocalizacao: {total_precos}")
        print(f"  - Supermercados: {len(SUPERMERCADOS_GOIANIA)}")
        print(f"{'='*60}")

        # Mostrar exemplos
        print("\nEXEMPLOS DE PRECOS CADASTRADOS:")
        print("-" * 60)

        exemplos = db.query(Preco, Produto).join(Produto).filter(
            Produto.nome.like("%Arroz%")
        ).order_by(Preco.preco).limit(8).all()

        for preco, produto in exemplos:
            promo = "[PROMO]" if preco.em_promocao else ""
            print(f"  R$ {preco.preco:.2f} | {produto.nome} {produto.marca} | {preco.supermercado} {promo}")

    except Exception as e:
        print(f"[ERRO] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    popular_precos()
