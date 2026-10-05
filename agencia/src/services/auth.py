import hashlib
from datetime import datetime, timedelta, timezone

import jwt

import config
from services.erros import CredenciaisInvalidas, TokenInvalido


def hash_senha(senha):
    # ponytail: sha256 sem salt; trocar por bcrypt/pbkdf2 se sair de projeto academico
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def gerar_token(sub, tipo, minutos=None):
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=config.JWT_EXPIRACAO_MINUTOS if minutos is None else minutos
    )
    payload = {"sub": str(sub), "tipo": tipo, "exp": expiracao}
    return jwt.encode(payload, config.JWT_SEGREDO, algorithm=config.JWT_ALGORITMO)


def decodificar_token(token):
    try:
        return jwt.decode(token, config.JWT_SEGREDO, algorithms=[config.JWT_ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise TokenInvalido("Token expirado.")
    except jwt.InvalidTokenError:
        raise TokenInvalido("Token invalido.")


class AuthService:
    def __init__(self, contas):
        self.contas = contas

    def login_cliente(self, id_conta, senha):
        conta = self.contas.buscar(id_conta)
        if not conta or conta.senha_hash != hash_senha(senha):
            raise CredenciaisInvalidas("Credenciais invalidas.")
        return self._sessao(sub=id_conta, tipo="cliente")

    def login_operador(self, usuario, senha):
        if usuario != config.OPERADOR_USUARIO or senha != config.OPERADOR_SENHA:
            raise CredenciaisInvalidas("Credenciais invalidas.")
        return self._sessao(sub=usuario, tipo="operador")

    def _sessao(self, sub, tipo):
        return {
            "token": gerar_token(sub=sub, tipo=tipo),
            "tipo": tipo,
            "expiraEmMinutos": config.JWT_EXPIRACAO_MINUTOS,
        }
