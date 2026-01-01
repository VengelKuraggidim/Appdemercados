"""
Buscador de Precos Locais
Busca precos em supermercados fisicos proximos ao usuario
Integra geolocalizacao com scrapers de redes conhecidas
"""
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import quote
import re

from .descobrir_supermercados import DescobrirSupermercados
from ..utils.geolocalizacao import GeoLocalizacao


class BuscadorPrecosLocais:
    """
    Busca precos em supermercados fisicos proximos ao usuario.

    1. Descobre supermercados proximos via OpenStreetMap
    2. Identifica redes conhecidas (Carrefour, Atacadao, etc.)
    3. Busca precos nessas redes usando seus sites
    4. Retorna produtos com localizacao real do supermercado mais proximo
    """

    # Mapeamento de nomes de supermercados para suas redes
    REDES_CONHECIDAS = {
        # Carrefour group
        'carrefour': 'carrefour',
        'carrefour bairro': 'carrefour',
        'carrefour express': 'carrefour',
        'carrefour market': 'carrefour',
        'atacadao': 'atacadao',
        'atacadão': 'atacadao',

        # GPA group
        'pao de acucar': 'pao_de_acucar',
        'pão de açúcar': 'pao_de_acucar',
        'extra': 'extra',
        'extra hiper': 'extra',
        'extra supermercado': 'extra',
        'minuto pao de acucar': 'pao_de_acucar',

        # Assai
        'assai': 'assai',
        'assaí': 'assai',
        'assai atacadista': 'assai',

        # Dia
        'dia': 'dia',
        'dia supermercado': 'dia',
        'dia%': 'dia',

        # Outros grandes
        'sonda': 'sonda',
        'sonda supermercados': 'sonda',
        'big': 'big',
        'big bompreco': 'big',
        'nacional': 'big',
        'mercadorama': 'big',
        'maxxi atacado': 'maxxi',
        'spani': 'spani',
        'savegnago': 'savegnago',
        'guanabara': 'guanabara',
        'prezunic': 'prezunic',
        'mundial': 'mundial',
        'supermarket': 'supermarket',
    }

    # URLs de busca por rede
    URLS_BUSCA = {
        'carrefour': 'https://www.carrefour.com.br/s?q={termo}',
        'atacadao': 'https://www.atacadao.com.br/busca?q={termo}',
        'extra': 'https://www.clubeextra.com.br/busca?q={termo}',
        'pao_de_acucar': 'https://www.paodeacucar.com/busca?q={termo}',
        'assai': 'https://www.assai.com.br/busca?q={termo}',
        'dia': 'https://www.dia.com.br/busca?q={termo}',
    }

    def __init__(self):
        self.descobridor = DescobrirSupermercados()
        self.geo = GeoLocalizacao()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def buscar(
        self,
        termo: str,
        latitude: float,
        longitude: float,
        raio_km: float = 10.0,
        limite: int = 30
    ) -> List[Dict]:
        """
        Busca precos em supermercados proximos ao usuario

        Args:
            termo: Termo de busca (ex: "arroz", "cafe")
            latitude: Latitude do usuario
            longitude: Longitude do usuario
            raio_km: Raio de busca em km (padrao: 10km)
            limite: Limite de produtos a retornar

        Returns:
            Lista de produtos com preco e localizacao
        """
        print(f"\n{'='*60}")
        print(f"[BUSCA LOCAL] BUSCANDO: '{termo}'")
        print(f"   Localizacao: ({latitude}, {longitude})")
        print(f"   Raio: {raio_km}km")
        print(f"{'='*60}")

        # 1. Descobrir supermercados proximos
        supermercados = self.descobridor.descobrir_por_gps(latitude, longitude, raio_km)

        if not supermercados:
            print("   [!] Nenhum supermercado encontrado na regiao")
            return []

        # 2. Identificar redes conhecidas e agrupar por rede
        redes_encontradas = self._identificar_redes(supermercados)

        if not redes_encontradas:
            print("   [!] Nenhuma rede conhecida encontrada")
            # Retorna os supermercados mesmo sem precos
            return self._criar_resultados_sem_preco(supermercados, termo)

        print(f"\n   Redes identificadas: {list(redes_encontradas.keys())}")

        # 3. Buscar precos em paralelo nas redes encontradas
        produtos = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}

            for rede, mercados in redes_encontradas.items():
                if rede in self.URLS_BUSCA:
                    future = executor.submit(
                        self._buscar_em_rede,
                        rede,
                        termo,
                        mercados
                    )
                    futures[future] = (rede, mercados)

            for future in as_completed(futures, timeout=30):
                rede, mercados = futures[future]
                try:
                    resultado = future.result()
                    if resultado:
                        produtos.extend(resultado)
                        print(f"   [OK] {rede}: {len(resultado)} produtos")
                    else:
                        print(f"   [!] {rede}: Nenhum resultado")
                except Exception as e:
                    print(f"   [X] {rede}: Erro - {str(e)[:50]}")

        # 4. Se nao encontrou precos nas redes, retornar supermercados proximos sem preco
        if not produtos:
            produtos = self._criar_resultados_sem_preco(supermercados[:15], termo)

        # 5. Ordenar por preco (None vai pro final)
        produtos.sort(key=lambda x: (x.get('preco') is None, x.get('preco') or float('inf')))

        # 5. Limitar resultados
        produtos = produtos[:limite]

        print(f"\n   [TOTAL] {len(produtos)} produtos encontrados em mercados proximos")
        print(f"{'='*60}")

        return produtos

    def _identificar_redes(self, supermercados: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Identifica quais supermercados pertencem a redes conhecidas

        Returns:
            Dicionario {rede: [lista de supermercados dessa rede]}
        """
        redes = {}

        for mercado in supermercados:
            nome = mercado.get('nome', '').lower()
            brand = mercado.get('brand', '').lower() if mercado.get('brand') else ''

            # Verificar se eh uma rede conhecida
            rede_identificada = None

            for padrao, rede in self.REDES_CONHECIDAS.items():
                if padrao in nome or padrao in brand:
                    rede_identificada = rede
                    break

            if rede_identificada:
                if rede_identificada not in redes:
                    redes[rede_identificada] = []
                redes[rede_identificada].append(mercado)

        return redes

    def _buscar_em_rede(
        self,
        rede: str,
        termo: str,
        mercados: List[Dict]
    ) -> List[Dict]:
        """
        Busca produtos em uma rede especifica e associa aos mercados proximos
        """
        if rede not in self.URLS_BUSCA:
            return []

        url_template = self.URLS_BUSCA[rede]
        url = url_template.format(termo=quote(termo))

        try:
            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code != 200:
                return []

            # Parse HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Buscar produtos usando seletores genericos
            produtos = self._extrair_produtos(soup, rede)

            # Associar cada produto ao mercado mais proximo dessa rede
            mercado_mais_proximo = mercados[0]  # Ja vem ordenado por distancia

            for produto in produtos:
                produto['supermercado'] = mercado_mais_proximo['nome']
                produto['latitude'] = mercado_mais_proximo['latitude']
                produto['longitude'] = mercado_mais_proximo['longitude']
                produto['distancia_km'] = mercado_mais_proximo['distancia_km']
                produto['endereco'] = mercado_mais_proximo.get('endereco')
                produto['rede'] = rede
                produto['fonte'] = 'supermercado_local'

            return produtos

        except Exception as e:
            print(f"      Erro buscando em {rede}: {e}")
            return []

    def _extrair_produtos(self, soup, rede: str) -> List[Dict]:
        """
        Extrai produtos do HTML usando seletores genericos
        """
        produtos = []

        # Seletores genericos que funcionam em varios sites
        card_selectors = [
            'div[data-testid="product-card"]',
            'article[class*="product"]',
            'div[class*="product-card"]',
            'li[class*="product"]',
            'div[class*="vtex-search"]',
            'div[class*="shelf-item"]',
            'div[class*="productCard"]',
        ]

        cards = []
        for selector in card_selectors:
            cards = soup.select(selector)
            if cards:
                break

        # Se nao encontrou com seletores especificos, tenta generico
        if not cards:
            cards = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower())

        for card in cards[:20]:  # Limite de 20 por rede
            try:
                produto = self._extrair_produto_card(card, rede)
                if produto:
                    produtos.append(produto)
            except:
                continue

        return produtos

    def _extrair_produto_card(self, card, rede: str) -> Optional[Dict]:
        """
        Extrai informacoes de um card de produto
        """
        # Nome
        nome = None
        for tag in ['h2', 'h3', 'h4']:
            elem = card.find(tag)
            if elem:
                nome = elem.get_text(strip=True)
                break

        if not nome:
            elem = card.select_one('[class*="name"], [class*="title"], [class*="productName"]')
            if elem:
                nome = elem.get_text(strip=True)

        if not nome or len(nome) < 3:
            return None

        # Preco
        preco = None
        preco_elem = card.select_one('[class*="price"], [class*="preco"], [class*="Price"]')

        if preco_elem:
            preco_text = preco_elem.get_text(strip=True)
            preco = self._limpar_preco(preco_text)

        if not preco:
            # Tenta encontrar qualquer texto com R$
            text = card.get_text()
            match = re.search(r'R\$\s*([\d.,]+)', text)
            if match:
                preco = self._limpar_preco(match.group(0))

        if not preco:
            return None

        # URL
        url = None
        link = card.find('a', href=True)
        if link:
            url = link['href']
            if url and not url.startswith('http'):
                # Adicionar dominio base
                bases = {
                    'carrefour': 'https://www.carrefour.com.br',
                    'atacadao': 'https://www.atacadao.com.br',
                    'extra': 'https://www.clubeextra.com.br',
                    'pao_de_acucar': 'https://www.paodeacucar.com',
                    'assai': 'https://www.assai.com.br',
                    'dia': 'https://www.dia.com.br',
                }
                base = bases.get(rede, '')
                url = base + url

        # Imagem
        imagem = None
        img = card.find('img', src=True)
        if img:
            imagem = img.get('src') or img.get('data-src')

        # Promocao
        em_promocao = bool(card.select_one('[class*="promo"], [class*="oferta"], [class*="desconto"], [class*="sale"]'))

        return {
            'nome': nome,
            'preco': preco,
            'url': url,
            'imagem': imagem,
            'em_promocao': em_promocao,
            'disponivel': True
        }

    def _limpar_preco(self, texto: str) -> Optional[float]:
        """
        Limpa e converte texto de preco para float
        """
        if not texto:
            return None

        # Remove caracteres nao numericos exceto , e .
        texto = re.sub(r'[^\d,.]', '', texto)

        if not texto:
            return None

        try:
            # Formato brasileiro: 1.234,56
            if ',' in texto:
                texto = texto.replace('.', '').replace(',', '.')

            preco = float(texto)

            # Validar preco razoavel (entre R$0.01 e R$50.000)
            if 0.01 <= preco <= 50000:
                return round(preco, 2)
        except:
            pass

        return None

    def _criar_resultados_sem_preco(self, supermercados: List[Dict], termo: str) -> List[Dict]:
        """
        Cria resultados indicando supermercados proximos com localizacao real.
        Mesmo sem preco online, o usuario pode visitar o supermercado.
        """
        resultados = []

        for mercado in supermercados[:15]:
            # Identificar a rede se possivel
            nome = mercado.get('nome', 'Supermercado')
            brand = mercado.get('brand')
            rede = self._identificar_rede_unica(nome, brand)

            resultados.append({
                'nome': f"Procurar '{termo}' em {nome}",
                'preco': None,
                'supermercado': nome,
                'rede': rede,
                'latitude': mercado['latitude'],
                'longitude': mercado['longitude'],
                'distancia_km': mercado['distancia_km'],
                'endereco': mercado.get('endereco'),
                'telefone': mercado.get('telefone'),
                'website': mercado.get('website'),
                'fonte': 'supermercado_local',
                'preco_indisponivel': True,
                'disponivel': True,
                'mensagem': f"Visite {nome} ({mercado['distancia_km']}km) para ver o preco"
            })

        return resultados

    def _identificar_rede_unica(self, nome: str, brand: str) -> Optional[str]:
        """Identifica a rede de um unico supermercado"""
        texto = f"{nome} {brand}".lower() if brand else nome.lower()

        for padrao, rede in self.REDES_CONHECIDAS.items():
            if padrao in texto:
                return rede

        return None


# Instancia global para uso facil
buscador_precos_locais = BuscadorPrecosLocais()


def buscar_precos_proximos(
    termo: str,
    latitude: float,
    longitude: float,
    raio_km: float = 10.0,
    limite: int = 30
) -> List[Dict]:
    """
    Funcao de conveniencia para buscar precos em supermercados proximos

    Args:
        termo: Termo de busca
        latitude: Latitude do usuario
        longitude: Longitude do usuario
        raio_km: Raio de busca em km
        limite: Limite de resultados

    Returns:
        Lista de produtos com preco e localizacao
    """
    return buscador_precos_locais.buscar(termo, latitude, longitude, raio_km, limite)
