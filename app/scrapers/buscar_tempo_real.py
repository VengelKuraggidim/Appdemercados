"""
Busca precos em tempo real de varias fontes
Nao usa banco de dados - busca diretamente na internet
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from urllib.parse import quote
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class BuscadorTempoReal:
    """Busca precos em tempo real de multiplas fontes"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9',
        }
        self.timeout = 15

    def buscar(self, termo: str, cidade: str = "Goiania", limite: int = 30) -> List[Dict]:
        """
        Busca precos em tempo real

        Args:
            termo: Produto a buscar (ex: "arroz 5kg")
            cidade: Cidade para filtrar resultados
            limite: Maximo de resultados

        Returns:
            Lista de produtos com precos
        """
        print(f"\n[TEMPO REAL] Buscando: '{termo}' em {cidade}")

        todos_produtos = []

        # Buscar em paralelo de varias fontes
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._buscar_mercadolivre, termo): 'Mercado Livre',
                executor.submit(self._buscar_buscape, termo): 'Buscape',
                executor.submit(self._buscar_zoom, termo): 'Zoom',
                executor.submit(self._buscar_duckduckgo, termo, cidade): 'DuckDuckGo',
                executor.submit(self._buscar_google_shopping, termo, cidade): 'Google Shopping',
            }

            for future in as_completed(futures, timeout=30):
                fonte = futures[future]
                try:
                    produtos = future.result()
                    if produtos:
                        todos_produtos.extend(produtos)
                        print(f"   [OK] {fonte}: {len(produtos)} produtos")
                except Exception as e:
                    print(f"   [ERRO] {fonte}: {e}")

        # Filtrar produtos irrelevantes
        produtos_relevantes = self._filtrar_relevantes(todos_produtos, termo)

        # Remover duplicatas e ordenar por preco
        produtos_unicos = self._remover_duplicatas(produtos_relevantes)
        produtos_unicos.sort(key=lambda x: x.get('preco', float('inf')))

        print(f"   [TOTAL] {len(produtos_unicos)} produtos unicos encontrados (de {len(todos_produtos)} brutos)")

        return produtos_unicos[:limite]

    def _buscar_mercadolivre(self, termo: str) -> List[Dict]:
        """Busca no Mercado Livre via API oficial"""
        produtos = []
        try:
            url = f"https://api.mercadolibre.com/sites/MLB/search"
            params = {'q': termo, 'limit': 15}

            # Usar headers para evitar bloqueio
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }

            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    preco = item.get('price', 0)
                    if preco and preco > 0:
                        produtos.append({
                            'nome': item.get('title', ''),
                            'preco': float(preco),
                            'preco_original': item.get('original_price'),
                            'em_promocao': item.get('original_price') is not None,
                            'url': item.get('permalink', ''),
                            'supermercado': 'Mercado Livre',
                            'imagem': item.get('thumbnail', ''),
                            'disponivel': item.get('available_quantity', 0) > 0,
                            'fonte': 'mercadolivre_api',
                            'tempo_real': True
                        })
        except Exception as e:
            print(f"      ML erro: {e}")

        return produtos

    def _buscar_google_shopping(self, termo: str, cidade: str) -> List[Dict]:
        """Busca no Google Shopping via scraping"""
        produtos = []
        try:
            query = f"{termo} supermercado {cidade}"
            url = f"https://www.google.com/search?q={quote(query)}&tbm=shop"

            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Procurar por precos
                texto = soup.get_text()
                matches = re.findall(r'R\$\s*([\d.,]+)', texto)

                for match in matches[:10]:
                    preco = self._limpar_preco(match)
                    if preco and 5 < preco < 100:
                        produtos.append({
                            'nome': f'{termo}',
                            'preco': preco,
                            'supermercado': 'Google Shopping',
                            'url': url,
                            'fonte': 'google_shopping',
                            'tempo_real': True,
                            'disponivel': True
                        })

        except Exception as e:
            print(f"      Google erro: {e}")

        return produtos[:5]

    def _buscar_buscape(self, termo: str) -> List[Dict]:
        """Busca no Buscape"""
        produtos = []
        try:
            url = f"https://www.buscape.com.br/search?q={quote(termo)}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Procurar cards de produto
                cards = soup.find_all('div', {'data-testid': True})

                for card in cards[:20]:
                    try:
                        # Extrair nome
                        nome_elem = card.find(['h2', 'h3', 'a'])
                        if not nome_elem:
                            continue
                        nome = nome_elem.get_text(strip=True)

                        if len(nome) < 5:
                            continue

                        # Extrair preco
                        preco = self._extrair_preco(card.get_text())
                        if not preco or preco > 500:  # Filtrar precos absurdos
                            continue

                        # Extrair loja
                        loja = 'Buscape'
                        loja_elem = card.find(class_=re.compile(r'store|seller|loja', re.I))
                        if loja_elem:
                            loja = loja_elem.get_text(strip=True)[:30]

                        produtos.append({
                            'nome': nome[:100],
                            'preco': preco,
                            'supermercado': loja,
                            'url': url,
                            'fonte': 'buscape',
                            'tempo_real': True,
                            'disponivel': True
                        })

                    except:
                        continue

        except Exception as e:
            print(f"      Buscape erro: {e}")

        return produtos

    def _buscar_zoom(self, termo: str) -> List[Dict]:
        """Busca no Zoom"""
        produtos = []
        try:
            url = f"https://www.zoom.com.br/search?q={quote(termo)}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Tentar encontrar cards de produto com precos
                cards = soup.find_all(['div', 'a'], class_=re.compile(r'product|card|item', re.I))

                for card in cards[:15]:
                    try:
                        texto = card.get_text()

                        # Extrair preco
                        preco_match = re.search(r'R\$\s*([\d.,]+)', texto)
                        if not preco_match:
                            continue

                        preco = self._limpar_preco(preco_match.group(1))

                        # Para alimentos, preco deve ser razoavel (R$ 5 a R$ 50)
                        if not preco or preco < 5 or preco > 50:
                            continue

                        # Extrair nome do produto
                        titulo = card.find(['h2', 'h3', 'a', 'span'])
                        nome = titulo.get_text(strip=True)[:80] if titulo else termo

                        produtos.append({
                            'nome': nome,
                            'preco': preco,
                            'supermercado': 'Zoom',
                            'url': url,
                            'fonte': 'zoom',
                            'tempo_real': True,
                            'disponivel': True
                        })

                    except:
                        continue

        except Exception as e:
            print(f"      Zoom erro: {e}")

        return produtos[:5]

    def _buscar_duckduckgo(self, termo: str, cidade: str) -> List[Dict]:
        """Busca no DuckDuckGo com filtro de cidade"""
        produtos = []
        try:
            query = f"{termo} preco supermercado {cidade}"
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"

            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Procurar resultados
                results = soup.find_all('div', class_='result')

                for result in results[:15]:
                    try:
                        texto = result.get_text()

                        # Extrair preco
                        preco = self._extrair_preco(texto)
                        if not preco or preco > 200:
                            continue

                        # Extrair titulo
                        titulo_elem = result.find('a', class_='result__a')
                        titulo = titulo_elem.get_text(strip=True) if titulo_elem else termo
                        url_result = titulo_elem.get('href', '') if titulo_elem else ''

                        # Identificar loja
                        loja = self._identificar_loja(texto, url_result)

                        produtos.append({
                            'nome': titulo[:100],
                            'preco': preco,
                            'supermercado': loja,
                            'url': url_result,
                            'fonte': 'duckduckgo',
                            'tempo_real': True,
                            'disponivel': True
                        })

                    except:
                        continue

        except Exception as e:
            print(f"      DDG erro: {e}")

        return produtos

    def _extrair_preco(self, texto: str) -> Optional[float]:
        """Extrai preco de um texto"""
        padroes = [
            r'R\$\s*([\d]+[.,][\d]{2})',
            r'([\d]+[.,][\d]{2})\s*(?:reais|R\$)',
            r'por\s*R?\$?\s*([\d]+[.,][\d]{2})',
        ]

        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return self._limpar_preco(match.group(1))

        return None

    def _limpar_preco(self, preco_str: str) -> Optional[float]:
        """Converte string de preco para float"""
        try:
            preco_str = preco_str.replace('.', '').replace(',', '.')
            preco = float(preco_str)
            if 0.01 <= preco <= 10000:
                return round(preco, 2)
        except:
            pass
        return None

    def _identificar_loja(self, texto: str, url: str) -> str:
        """Identifica a loja a partir do texto ou URL"""
        texto_lower = (texto + url).lower()

        lojas = {
            'carrefour': 'Carrefour',
            'paodeacucar': 'Pao de Acucar',
            'extra': 'Extra',
            'atacadao': 'Atacadao',
            'assai': 'Assai',
            'mercadolivre': 'Mercado Livre',
            'americanas': 'Americanas',
            'magazine': 'Magazine Luiza',
            'casasbahia': 'Casas Bahia',
            'tatico': 'Tatico',
            'bretas': 'Bretas',
        }

        for chave, nome in lojas.items():
            if chave in texto_lower.replace(' ', '').replace('-', ''):
                return nome

        return 'Loja Online'

    def _filtrar_relevantes(self, produtos: List[Dict], termo: str) -> List[Dict]:
        """Filtra produtos irrelevantes baseado no termo buscado"""
        termo_lower = termo.lower()
        palavras_termo = set(termo_lower.split())

        # Palavras que indicam que o produto NAO e o que estamos buscando
        palavras_irrelevantes = {
            'cao', 'cachorro', 'gato', 'pet', 'racao', 'ração',
            'shampoo', 'condicionador', 'creme', 'sabonete',
            'brinquedo', 'roupa', 'calcado', 'sapato',
            'celular', 'smartphone', 'notebook', 'tablet',
            'eletronico', 'eletrodomestico'
        }

        filtrados = []
        for p in produtos:
            nome = p.get('nome', '').lower()

            # Verificar se tem palavras irrelevantes
            tem_irrelevante = False
            for palavra in palavras_irrelevantes:
                if palavra in nome and palavra not in termo_lower:
                    tem_irrelevante = True
                    break

            if tem_irrelevante:
                continue

            # Verificar se pelo menos uma palavra do termo esta no nome
            tem_palavra_termo = False
            for palavra in palavras_termo:
                if len(palavra) > 2 and palavra in nome:
                    tem_palavra_termo = True
                    break

            # Se nao tem nenhuma palavra do termo, e o nome e muito diferente, pular
            if not tem_palavra_termo and len(nome) > 20:
                # Verificar similaridade basica
                palavras_nome = set(nome.split())
                intersecao = palavras_termo & palavras_nome
                if len(intersecao) == 0:
                    continue

            filtrados.append(p)

        return filtrados

    def _remover_duplicatas(self, produtos: List[Dict]) -> List[Dict]:
        """Remove produtos duplicados mantendo o menor preco"""
        unicos = {}

        for p in produtos:
            # Criar chave unica baseada no nome normalizado
            nome_norm = re.sub(r'[^a-z0-9]', '', p.get('nome', '').lower())[:30]
            chave = nome_norm

            if chave not in unicos or p.get('preco', float('inf')) < unicos[chave].get('preco', float('inf')):
                unicos[chave] = p

        return list(unicos.values())


# Instancia global
buscador_tempo_real = BuscadorTempoReal()


def buscar_precos_tempo_real(termo: str, cidade: str = "Goiania", limite: int = 30) -> List[Dict]:
    """Funcao de conveniencia para buscar precos em tempo real"""
    return buscador_tempo_real.buscar(termo, cidade, limite)


# Teste
if __name__ == "__main__":
    produtos = buscar_precos_tempo_real("arroz 5kg", "Goiania")

    print("\n" + "=" * 60)
    print("RESULTADOS:")
    print("=" * 60)

    for i, p in enumerate(produtos[:15], 1):
        print(f"{i}. R$ {p['preco']:.2f} | {p['nome'][:40]} | {p['supermercado']}")
