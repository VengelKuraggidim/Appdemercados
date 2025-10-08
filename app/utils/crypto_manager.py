from sqlalchemy.orm import Session
from app.models.database import Carteira, Transacao
from datetime import datetime
import hashlib


class ReputacaoManager:
    """Gerenciador centralizado de reputação

    Sistema de pontos balanceado:
    - Validações de preços: +2 a +10 pontos (baseado em consenso)
    - Sugestão aprovada pela DAO: +15 pontos
    - Sugestão implementada: +25 pontos
    - Votar em sugestão: +1 ponto
    - Comentário na DAO: +0.5 pontos (máximo 5 por dia)
    - Sugestão rejeitada: -5 pontos
    - Validação incorreta (contra consenso): -3 pontos
    """

    # Pontos por ação
    VALIDACAO_PRECO_CORRETA = 2  # Quando valida corretamente (consenso > 70%)
    VALIDACAO_PRECO_INCORRETA = -3  # Quando valida contra consenso
    SUGESTAO_APROVADA = 15  # Quando sugestão atinge 60% de aprovação
    SUGESTAO_IMPLEMENTADA = 25  # Quando sugestão é marcada como implementada
    SUGESTAO_REJEITADA = -5  # Quando sugestão é rejeitada
    VOTO_SUGESTAO = 1  # Por participar da votação
    COMENTARIO_DAO = 0.5  # Por comentário (limitado por dia)
    MAX_COMENTARIOS_DIA = 5  # Limite de comentários que ganham reputação por dia

    # Limites de reputação
    REPUTACAO_MINIMA = 0
    REPUTACAO_MAXIMA = 200

    def __init__(self, db: Session):
        self.db = db

    def adicionar_reputacao(self, usuario_nome: str, pontos: float, motivo: str) -> dict:
        """Adiciona ou remove pontos de reputação de um usuário"""
        from app.models.database import Carteira

        carteira = self.db.query(Carteira).filter(
            Carteira.usuario_nome == usuario_nome
        ).first()

        if not carteira:
            return {
                "sucesso": False,
                "mensagem": "Usuário não encontrado"
            }

        reputacao_antiga = carteira.reputacao or 100
        carteira.reputacao = max(
            self.REPUTACAO_MINIMA,
            min(self.REPUTACAO_MAXIMA, reputacao_antiga + pontos)
        )

        self.db.commit()

        return {
            "sucesso": True,
            "reputacao_antiga": reputacao_antiga,
            "reputacao_nova": carteira.reputacao,
            "pontos_ganhos": pontos,
            "motivo": motivo
        }

    def pode_ganhar_reputacao_comentario(self, usuario_nome: str) -> bool:
        """Verifica se usuário pode ganhar reputação por comentário hoje"""
        from app.models.database import Comentario
        from sqlalchemy import func

        hoje = datetime.now().date()

        # Contar comentários de hoje
        comentarios_hoje = self.db.query(func.count(Comentario.id)).filter(
            Comentario.usuario_nome == usuario_nome,
            func.date(Comentario.data_criacao) == hoje
        ).scalar()

        return comentarios_hoje < self.MAX_COMENTARIOS_DIA

    def calcular_reputacao_comentario(self, comentario_id: int) -> dict:
        """
        Calcula e atualiza reputação do autor do comentário baseado em likes/dislikes

        Fórmula:
        - Se likes > dislikes: ganha (likes - dislikes) / total_votos * 0.1 pontos
        - Se dislikes > likes: perde (dislikes - likes) / total_votos * 0.1 pontos

        Exemplo:
        - 10 likes, 1 dislike: +0.09 pts ((10-1)/100 * 1 = 0.09)
        - 11 likes, 22 dislikes: -0.11 pts ((22-11)/100 * 1 = -0.11)
        """
        from app.models.database import Comentario, VotoComentario
        from sqlalchemy import func

        comentario = self.db.query(Comentario).filter(Comentario.id == comentario_id).first()
        if not comentario:
            return {"sucesso": False, "mensagem": "Comentário não encontrado"}

        # Contar likes e dislikes
        likes = self.db.query(func.count(VotoComentario.id)).filter(
            VotoComentario.comentario_id == comentario_id,
            VotoComentario.tipo == "like"
        ).scalar() or 0

        dislikes = self.db.query(func.count(VotoComentario.id)).filter(
            VotoComentario.comentario_id == comentario_id,
            VotoComentario.tipo == "dislike"
        ).scalar() or 0

        total_votos = likes + dislikes

        if total_votos == 0:
            return {
                "sucesso": True,
                "mensagem": "Sem votos ainda",
                "alteracao": 0,
                "likes": 0,
                "dislikes": 0
            }

        # Calcular diferença
        diferenca = likes - dislikes

        # Fórmula: (diferença / total) * 0.1
        # Se diferenca positiva: ganha reputação
        # Se diferenca negativa: perde reputação
        alteracao = round((diferenca / total_votos) * 0.1, 2)

        # Atualizar reputação (sem acumular - usa valor absoluto do cálculo)
        if alteracao != 0:
            resultado = self.adicionar_reputacao(
                comentario.usuario_nome,
                alteracao,
                f"Votação em comentário ({likes}👍 / {dislikes}👎)"
            )

            return {
                "sucesso": True,
                "mensagem": f"Reputação atualizada: {alteracao:+.2f} pts",
                "alteracao": alteracao,
                "likes": likes,
                "dislikes": dislikes,
                "total_votos": total_votos
            }
        else:
            return {
                "sucesso": True,
                "mensagem": "Votos empatados, sem alteração",
                "alteracao": 0,
                "likes": likes,
                "dislikes": dislikes,
                "total_votos": total_votos
            }

    def validar_preco_automaticamente(self, preco_id: int) -> dict:
        """
        Valida um preço automaticamente comparando com outros preços do mesmo produto

        Lógica:
        - Se o preço está próximo da mediana (± 30%): +2 reputação
        - Se o preço está muito diferente da mediana (> 50%): -5 reputação
        - Precisa de pelo menos 2 outros preços para comparar
        """
        from app.models.database import Preco, Produto, Carteira
        from sqlalchemy import func
        from datetime import timedelta
        import statistics

        # Buscar o preço adicionado
        preco_novo = self.db.query(Preco).filter(Preco.id == preco_id).first()
        if not preco_novo or not preco_novo.manual:
            return {"sucesso": False, "mensagem": "Preço não encontrado ou não é manual"}

        # Buscar outros preços do mesmo produto (últimos 30 dias)
        data_limite = datetime.now() - timedelta(days=30)
        outros_precos = self.db.query(Preco).filter(
            Preco.produto_id == preco_novo.produto_id,
            Preco.id != preco_id,
            Preco.data_coleta >= data_limite,
            Preco.preco > 0  # Ignorar preços inválidos
        ).all()

        # Precisa de pelo menos 2 outros preços para comparar
        if len(outros_precos) < 2:
            return {
                "sucesso": True,
                "mensagem": "Poucos preços para comparar, sem alteração de reputação",
                "alteracao_reputacao": 0
            }

        # Calcular mediana dos outros preços
        precos_valores = [p.preco for p in outros_precos]
        mediana = statistics.median(precos_valores)

        # Calcular diferença percentual
        diferenca_percentual = abs((preco_novo.preco - mediana) / mediana) * 100

        # Decidir reputação
        if diferenca_percentual <= 30:
            # Preço próximo da média: +2 pontos
            resultado = self.adicionar_reputacao(
                preco_novo.usuario_nome,
                2,
                f"Preço válido (±{diferenca_percentual:.1f}% da média)"
            )
            return {
                "sucesso": True,
                "mensagem": f"✅ Preço validado! Próximo da média ({diferenca_percentual:.1f}% de diferença)",
                "alteracao_reputacao": 2,
                "diferenca_percentual": diferenca_percentual,
                "mediana": mediana
            }
        elif diferenca_percentual > 50:
            # Preço muito diferente: -5 pontos
            resultado = self.adicionar_reputacao(
                preco_novo.usuario_nome,
                -5,
                f"Preço suspeito ({diferenca_percentual:.1f}% diferente da média)"
            )
            return {
                "sucesso": True,
                "mensagem": f"⚠️ Preço muito diferente da média ({diferenca_percentual:.1f}% de diferença)",
                "alteracao_reputacao": -5,
                "diferenca_percentual": diferenca_percentual,
                "mediana": mediana
            }
        else:
            # Preço aceitável mas não muito próximo: sem alteração
            return {
                "sucesso": True,
                "mensagem": f"Preço aceitável ({diferenca_percentual:.1f}% de diferença)",
                "alteracao_reputacao": 0,
                "diferenca_percentual": diferenca_percentual,
                "mediana": mediana
            }


class CryptoManager:
    """Gerenciador de criptomoeda do app"""

    # Constantes de recompensas
    RECOMPENSA_CONTRIBUICAO = 10.0
    CUSTO_BUSCA = 1.0
    BONUS_PRIMEIRO_ACESSO = 5.0

    def __init__(self, db: Session):
        self.db = db

    def criar_ou_obter_carteira(self, usuario_nome: str, cpf: str = None, senha: str = None) -> Carteira:
        """Cria carteira se não existir ou retorna a existente"""
        carteira = self.db.query(Carteira).filter(
            Carteira.usuario_nome == usuario_nome
        ).first()

        if not carteira:
            senha_hash = self._hash_senha(senha) if senha else None
            carteira = Carteira(
                usuario_nome=usuario_nome,
                cpf=cpf,
                senha_hash=senha_hash,
                saldo=self.BONUS_PRIMEIRO_ACESSO
            )
            self.db.add(carteira)
            self.db.flush()

            # Registrar bônus inicial
            self._registrar_transacao(
                carteira_id=carteira.id,
                tipo="bonus",
                quantidade=self.BONUS_PRIMEIRO_ACESSO,
                descricao="Bônus de boas-vindas"
            )

        return carteira

    def autenticar(self, cpf: str, senha: str) -> dict:
        """Autentica usuário com CPF e senha"""
        carteira = self.db.query(Carteira).filter(
            Carteira.cpf == cpf
        ).first()

        if not carteira:
            return {
                "sucesso": False,
                "mensagem": "CPF não cadastrado"
            }

        senha_hash = self._hash_senha(senha)
        if carteira.senha_hash != senha_hash:
            return {
                "sucesso": False,
                "mensagem": "Senha incorreta"
            }

        return {
            "sucesso": True,
            "mensagem": "Login realizado com sucesso!",
            "usuario_nome": carteira.usuario_nome,
            "saldo": carteira.saldo
        }

    def _hash_senha(self, senha: str) -> str:
        """Hash simples de senha (em produção usar bcrypt)"""
        return hashlib.sha256(senha.encode()).hexdigest()

    def minerar_tokens(self, usuario_nome: str, preco_id: int = None) -> dict:
        """Recompensa usuário por contribuir com preço"""
        carteira = self.criar_ou_obter_carteira(usuario_nome)

        # Adicionar tokens
        carteira.saldo += self.RECOMPENSA_CONTRIBUICAO
        carteira.ultima_atualizacao = datetime.now()

        # Registrar transação
        self._registrar_transacao(
            carteira_id=carteira.id,
            tipo="mineracao",
            quantidade=self.RECOMPENSA_CONTRIBUICAO,
            descricao="Recompensa por adicionar preço",
            preco_id=preco_id
        )

        self.db.commit()

        return {
            "sucesso": True,
            "mensagem": f"Você minerou {self.RECOMPENSA_CONTRIBUICAO} tokens!",
            "saldo_atual": carteira.saldo,
            "tokens_ganhos": self.RECOMPENSA_CONTRIBUICAO
        }

    def gastar_tokens(self, usuario_nome: str, quantidade: float = None, descricao: str = "Busca de produto") -> dict:
        """Gasta tokens do usuário (busca ou outra ação)"""
        if quantidade is None:
            quantidade = self.CUSTO_BUSCA

        carteira = self.criar_ou_obter_carteira(usuario_nome)

        # Verificar se tem saldo suficiente
        if carteira.saldo < quantidade:
            return {
                "sucesso": False,
                "mensagem": f"Saldo insuficiente! Você tem {carteira.saldo} tokens mas precisa de {quantidade}",
                "saldo_atual": carteira.saldo,
                "faltam": quantidade - carteira.saldo
            }

        # Deduzir tokens
        carteira.saldo -= quantidade
        carteira.ultima_atualizacao = datetime.now()

        # Registrar transação (quantidade negativa)
        self._registrar_transacao(
            carteira_id=carteira.id,
            tipo="busca",
            quantidade=-quantidade,
            descricao=descricao
        )

        self.db.commit()

        return {
            "sucesso": True,
            "mensagem": f"Busca realizada! Custo: {quantidade} tokens",
            "saldo_atual": carteira.saldo,
            "tokens_gastos": quantidade
        }

    def obter_saldo(self, usuario_nome: str) -> dict:
        """Retorna saldo e estatísticas da carteira"""
        carteira = self.criar_ou_obter_carteira(usuario_nome)

        # Calcular estatísticas
        transacoes = self.db.query(Transacao).filter(
            Transacao.carteira_id == carteira.id
        ).all()

        total_minerado = sum(t.quantidade for t in transacoes if t.quantidade > 0)
        total_gasto = abs(sum(t.quantidade for t in transacoes if t.quantidade < 0))

        return {
            "usuario_nome": carteira.usuario_nome,
            "saldo": carteira.saldo,
            "total_minerado": total_minerado,
            "total_gasto": total_gasto,
            "ultima_atualizacao": carteira.ultima_atualizacao,
            "total_transacoes": len(transacoes),
            # Reputação
            "reputacao": carteira.reputacao,
            "total_validacoes_feitas": carteira.total_validacoes_feitas,
            "total_validacoes_recebidas": carteira.total_validacoes_recebidas,
            "validacoes_positivas": carteira.validacoes_positivas,
            "validacoes_negativas": carteira.validacoes_negativas
        }

    def obter_historico(self, usuario_nome: str, limite: int = 50) -> list:
        """Retorna histórico de transações"""
        carteira = self.criar_ou_obter_carteira(usuario_nome)

        transacoes = self.db.query(Transacao).filter(
            Transacao.carteira_id == carteira.id
        ).order_by(Transacao.data_transacao.desc()).limit(limite).all()

        return transacoes

    def _registrar_transacao(self, carteira_id: int, tipo: str, quantidade: float,
                            descricao: str = None, preco_id: int = None):
        """Registra uma transação no histórico"""
        transacao = Transacao(
            carteira_id=carteira_id,
            tipo=tipo,
            quantidade=quantidade,
            descricao=descricao,
            preco_id=preco_id,
            data_transacao=datetime.now()
        )
        self.db.add(transacao)

    def verificar_saldo_suficiente(self, usuario_nome: str, quantidade: float = None) -> bool:
        """Verifica se usuário tem saldo suficiente"""
        if quantidade is None:
            quantidade = self.CUSTO_BUSCA

        carteira = self.criar_ou_obter_carteira(usuario_nome)
        return carteira.saldo >= quantidade
