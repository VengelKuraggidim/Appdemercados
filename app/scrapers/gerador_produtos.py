"""
Gerador de Produtos Sob Demanda
Gera produtos realistas baseado na busca do usuário
Simula scraping em tempo real
"""
from typing import List, Dict
import random
import hashlib


class GeradorProdutos:
    """
    Gera produtos realistas baseado no termo de busca
    Cada busca gera resultados consistentes (mesmo termo = mesmos produtos)
    """

    def __init__(self):
        self.supermercados = [
            'Carrefour',
            'Pão de Açúcar',
            'Extra',
            'Mercado Livre',
            'Americanas',
            'Shopee'
        ]

        # Banco de marcas por categoria
        self.marcas = {
            'arroz': ['Tio João', 'Uncle Bens', 'Camil', 'Prato Fino', 'Blue Ville', 'Vapza'],
            'feijão': ['Camil', 'Kicaldo', 'Tio João', 'Combrasil', 'Vapza'],
            'café': ['Pilão', '3 Corações', 'Melitta', 'Caboclo', 'Café do Ponto'],
            'leite': ['Parmalat', 'Italac', 'Piracanjuba', 'Ninho', 'Elegê'],
            'óleo': ['Liza', 'Soya', 'Concordia', 'ABC', 'Sinhá'],
            'açúcar': ['União', 'Guarani', 'Caravelas', 'Alto Alegre', 'Cristal'],
            'macarrão': ['Galo', 'Adria', 'Basilar', 'Renata', 'Santa Amália'],
            'farinha': ['Dona Benta', 'Qualitá', 'Sol', 'Anaconda'],
            'chocolate': ['Lacta', 'Nestlé', 'Garoto', 'Hersheys', 'Cacau Show'],
            'sabão': ['Omo', 'Ariel', 'Tixan', 'Ace', 'Surf'],
            'sabonete': ['Dove', 'Lux', 'Protex', 'Rexona', 'Palmolive'],
            'shampoo': ['Pantene', 'Dove', 'Seda', 'Clear', 'TRESemmé'],
            'default': ['Qualitá', 'Marca Própria', 'Leader', 'Great Value']
        }

        # Variações de peso/tamanho
        self.tamanhos = {
            'arroz': ['1kg', '2kg', '5kg'],
            'feijão': ['1kg', '2kg'],
            'café': ['250g', '500g', '1kg'],
            'leite': ['1L', '1L Integral', '1L Desnatado'],
            'óleo': ['900ml', '1L'],
            'açúcar': ['1kg', '2kg', '5kg'],
            'macarrão': ['500g', '1kg'],
            'farinha': ['1kg', '5kg'],
            'chocolate': ['90g', '150g', '200g', 'Caixa 300g'],
            'sabão': ['1kg', '2kg', 'Caixa 1kg'],
            'sabonete': '90g',
            'shampoo': ['200ml', '400ml', '750ml'],
            'default': ['unidade', 'pacote']
        }

        # Faixas de preço base por categoria
        self.precos_base = {
            'arroz': (15, 35),
            'feijão': (8, 18),
            'café': (8, 25),
            'leite': (4, 8),
            'óleo': (6, 12),
            'açúcar': (3, 8),
            'macarrão': (3, 8),
            'farinha': (4, 10),
            'chocolate': (5, 20),
            'sabão': (10, 25),
            'sabonete': (2, 6),
            'shampoo': (8, 30),
            'default': (5, 50)
        }

    def _get_seed(self, termo: str, index: int) -> int:
        """Gera seed consistente para termo + index"""
        hash_str = f"{termo.lower()}_{index}"
        return int(hashlib.md5(hash_str.encode()).hexdigest()[:8], 16)

    def _detectar_categoria(self, termo: str) -> str:
        """Detecta categoria do termo de busca"""
        termo_lower = termo.lower()

        for categoria in self.marcas.keys():
            if categoria in termo_lower:
                return categoria

        return 'default'

    def gerar_produtos(self, termo: str, quantidade: int = 15) -> List[Dict]:
        """
        Gera produtos baseado no termo de busca
        Sempre retorna os mesmos produtos para o mesmo termo
        """
        print(f"\n{'='*60}")
        print(f"🎲 GERADOR DE PRODUTOS: '{termo}'")
        print(f"{'='*60}")

        categoria = self._detectar_categoria(termo)
        marcas = self.marcas.get(categoria, self.marcas['default'])
        tamanhos = self.tamanhos.get(categoria, self.tamanhos['default'])
        preco_min, preco_max = self.precos_base.get(categoria, self.precos_base['default'])

        produtos = []

        for i in range(quantidade):
            # Usar seed para resultados consistentes
            seed = self._get_seed(termo, i)
            random.seed(seed)

            # Escolher marca
            marca = random.choice(marcas)

            # Escolher tamanho
            if isinstance(tamanhos, list):
                tamanho = random.choice(tamanhos)
            else:
                tamanho = tamanhos

            # Gerar nome do produto
            nome = f"{marca} {termo.title()} {tamanho}"

            # Gerar preço
            preco = round(random.uniform(preco_min, preco_max), 2)

            # 30% chance de estar em promoção
            em_promocao = random.random() < 0.3
            preco_original = None

            if em_promocao:
                # Desconto entre 10% e 40%
                desconto = random.uniform(0.10, 0.40)
                preco_original = round(preco / (1 - desconto), 2)

            # Escolher supermercado
            supermercado = random.choice(self.supermercados)

            # Gerar URL fake mas realista
            url_slug = termo.lower().replace(' ', '-')
            url = f"https://www.{supermercado.lower().replace(' ', '')}.com.br/produto/{url_slug}-{marca.lower().replace(' ', '-')}-{i}"

            produtos.append({
                'nome': nome,
                'marca': marca,
                'preco': preco,
                'preco_original': preco_original,
                'em_promocao': em_promocao,
                'url': url,
                'supermercado': supermercado,
                'disponivel': True,
                'fonte': 'gerador_sob_demanda'
            })

        # Resetar seed
        random.seed()

        print(f"   ✅ Gerados {len(produtos)} produtos para '{termo}'")
        print(f"   📊 Categoria detectada: {categoria}")
        print(f"   💰 Faixa de preço: R$ {preco_min:.2f} - R$ {preco_max:.2f}")
        print(f"{'='*60}\n")

        return produtos

    def gerar_por_supermercado(self, termo: str, supermercado: str, quantidade: int = 10) -> List[Dict]:
        """Gera produtos de um supermercado específico"""
        todos = self.gerar_produtos(termo, quantidade * 2)
        return [p for p in todos if p['supermercado'] == supermercado][:quantidade]

    def adicionar_categoria(self, categoria: str, marcas: List[str], tamanhos: List[str], preco_min: float, preco_max: float):
        """Permite adicionar novas categorias dinamicamente"""
        self.marcas[categoria] = marcas
        self.tamanhos[categoria] = tamanhos
        self.precos_base[categoria] = (preco_min, preco_max)


# Instância global
gerador_produtos = GeradorProdutos()


# Função auxiliar para expandir categorias automaticamente
def expandir_categorias():
    """Adiciona mais categorias comuns"""
    gerador = gerador_produtos

    # Alimentos
    gerador.adicionar_categoria('carne', ['Friboi', 'Swift', 'Seara', 'Sadia'], ['1kg', '500g'], 20, 60)
    gerador.adicionar_categoria('frango', ['Seara', 'Sadia', 'Perdigão', 'Aurora'], ['1kg', '2kg'], 12, 25)
    gerador.adicionar_categoria('pão', ['Wickbold', 'Pullman', 'Seven Boys', 'Nutrella'], ['500g', '650g'], 5, 12)
    gerador.adicionar_categoria('manteiga', ['Itambé', 'Aviação', 'Vigor', 'Paulista'], ['200g', '500g'], 8, 18)
    gerador.adicionar_categoria('queijo', ['Tirolez', 'Polenghi', 'Vigor', 'Danúbio'], ['150g', '400g'], 10, 25)

    # Bebidas
    gerador.adicionar_categoria('refrigerante', ['Coca-Cola', 'Pepsi', 'Guaraná Antarctica', 'Fanta'], ['2L', '1L', '600ml'], 5, 12)
    gerador.adicionar_categoria('suco', ['Del Valle', 'Maguary', 'Dafruta', 'Tang'], ['1L', '500ml'], 4, 10)
    gerador.adicionar_categoria('cerveja', ['Skol', 'Brahma', 'Heineken', 'Budweiser'], ['Lata 350ml', 'Long Neck', 'Garrafa 600ml'], 3, 8)

    # Limpeza
    gerador.adicionar_categoria('detergente', ['Ypê', 'Limpol', 'Minuano', 'Clear'], ['500ml', '1L'], 2, 5)
    gerador.adicionar_categoria('água sanitária', ['Qboa', 'Candura', 'Super Globo'], ['1L', '2L'], 3, 7)
    gerador.adicionar_categoria('amaciante', ['Comfort', 'Fofo', 'Mon Bijou', 'Ypê'], ['1L', '2L'], 6, 15)

    # Higiene
    gerador.adicionar_categoria('pasta de dente', ['Colgate', 'Oral-B', 'Sorriso', 'Close Up'], ['90g', '140g'], 4, 10)
    gerador.adicionar_categoria('papel higiênico', ['Personal', 'Neve', 'Sublime', 'Fofura'], ['12 rolos', '4 rolos'], 8, 20)


# Expandir automaticamente ao importar
expandir_categorias()
