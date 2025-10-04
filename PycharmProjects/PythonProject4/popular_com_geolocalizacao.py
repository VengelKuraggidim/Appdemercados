"""
Script para popular banco de dados com produtos COM geolocalização
para testar a funcionalidade de análise de custo-benefício
"""
from app.models.database import SessionLocal, Produto, Preco
from datetime import datetime

def popular_produtos_com_geo():
    db = SessionLocal()

    try:
        # Limpar preços antigos
        print("🗑️  Limpando dados antigos...")
        db.query(Preco).delete()
        db.query(Produto).delete()
        db.commit()

        # Criar produtos
        print("📦 Criando produtos...")

        produtos_data = [
            {"nome": "Arroz Tio João 5kg", "marca": "Tio João"},
            {"nome": "Feijão Camil 1kg", "marca": "Camil"},
            {"nome": "Óleo Liza 900ml", "marca": "Liza"},
            {"nome": "Açúcar União 1kg", "marca": "União"},
            {"nome": "Café Pilão 500g", "marca": "Pilão"},
            {"nome": "Macarrão Barilla 500g", "marca": "Barilla"},
        ]

        produtos = []
        for p_data in produtos_data:
            produto = Produto(**p_data, categoria="Alimentos")
            db.add(produto)
            produtos.append(produto)

        db.commit()
        print(f"✅ {len(produtos)} produtos criados!")

        # Criar preços com GEOLOCALIZAÇÃO
        # Coordenadas de exemplo (São Paulo)
        locais = {
            "Carrefour": {
                "lat": -23.5505,  # Av. Paulista
                "lon": -46.6333,
                "endereco": "Av. Paulista, 1000 - Bela Vista, São Paulo"
            },
            "Atacadão": {
                "lat": -23.5489,  # Próximo, mas diferente
                "lon": -46.6388,
                "endereco": "R. da Consolação, 500 - Consolação, São Paulo"
            },
            "Extra": {
                "lat": -23.5650,  # Mais longe
                "lon": -46.6520,
                "endereco": "Av. Rebouças, 3970 - Pinheiros, São Paulo"
            },
            "Pão de Açúcar": {
                "lat": -23.5420,  # Outra direção
                "lon": -46.6250,
                "endereco": "R. Augusta, 2690 - Jardins, São Paulo"
            }
        }

        print("\n📍 Adicionando preços com geolocalização...")

        precos_data = [
            # Arroz
            {"produto_idx": 0, "super": "Carrefour", "preco": 22.90},
            {"produto_idx": 0, "super": "Atacadão", "preco": 18.90},
            {"produto_idx": 0, "super": "Extra", "preco": 24.50},
            {"produto_idx": 0, "super": "Pão de Açúcar", "preco": 25.90},

            # Feijão
            {"produto_idx": 1, "super": "Carrefour", "preco": 8.90},
            {"produto_idx": 1, "super": "Atacadão", "preco": 7.50},
            {"produto_idx": 1, "super": "Extra", "preco": 9.20},
            {"produto_idx": 1, "super": "Pão de Açúcar", "preco": 9.90},

            # Óleo
            {"produto_idx": 2, "super": "Carrefour", "preco": 6.90},
            {"produto_idx": 2, "super": "Atacadão", "preco": 5.90},
            {"produto_idx": 2, "super": "Extra", "preco": 7.50},
            {"produto_idx": 2, "super": "Pão de Açúcar", "preco": 7.90},

            # Açúcar
            {"produto_idx": 3, "super": "Carrefour", "preco": 4.90},
            {"produto_idx": 3, "super": "Atacadão", "preco": 3.90},
            {"produto_idx": 3, "super": "Extra", "preco": 5.20},
            {"produto_idx": 3, "super": "Pão de Açúcar", "preco": 5.50},

            # Café
            {"produto_idx": 4, "super": "Carrefour", "preco": 15.90},
            {"produto_idx": 4, "super": "Atacadão", "preco": 13.50},
            {"produto_idx": 4, "super": "Extra", "preco": 16.90},
            {"produto_idx": 4, "super": "Pão de Açúcar", "preco": 17.50},

            # Macarrão
            {"produto_idx": 5, "super": "Carrefour", "preco": 4.50},
            {"produto_idx": 5, "super": "Atacadão", "preco": 3.90},
            {"produto_idx": 5, "super": "Extra", "preco": 4.90},
            {"produto_idx": 5, "super": "Pão de Açúcar", "preco": 5.20},
        ]

        for p_data in precos_data:
            local_info = locais[p_data["super"]]

            preco = Preco(
                produto_id=produtos[p_data["produto_idx"]].id,
                supermercado=p_data["super"].lower().replace(" ", "_").replace("ã", "a").replace("ú", "u"),
                preco=p_data["preco"],
                em_promocao=False,
                manual=True,
                usuario_nome="Sistema",
                localizacao=local_info["endereco"],
                latitude=local_info["lat"],
                longitude=local_info["lon"],
                endereco=local_info["endereco"],
                disponivel=True,
                verificado=True,
                data_coleta=datetime.now()
            )
            db.add(preco)

        db.commit()
        print(f"✅ {len(precos_data)} preços adicionados com geolocalização!")

        print("\n" + "="*60)
        print("🎉 BANCO POPULADO COM SUCESSO!")
        print("="*60)
        print("\n📋 Resumo:")
        print(f"   • {len(produtos)} produtos")
        print(f"   • {len(precos_data)} preços")
        print(f"   • {len(locais)} supermercados com localização")
        print("\n🧪 Teste agora:")
        print("   1. Acesse: http://localhost:8000")
        print("   2. Permita acesso à localização")
        print("   3. Marque o checkbox de busca otimizada")
        print("   4. Busque: arroz, feijão, óleo, etc.")
        print("\n💡 Localização de teste (São Paulo - Paulista):")
        print("   Latitude: -23.5505")
        print("   Longitude: -46.6333")
        print("\n")

    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    popular_produtos_com_geo()
