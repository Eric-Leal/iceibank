import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import config

esquema_bearer = HTTPBearer(auto_error=False)


def hash_senha(senha):
    # ponytail: sha256 sem salt; trocar por bcrypt/pbkdf2 se sair de projeto academico
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def gerar_token(sub, tipo, minutos=None):
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=config.JWT_EXPIRACAO_MINUTOS if minutos is None else minutos
    )
    payload = {"sub": str(sub), "tipo": tipo, "exp": expiracao}
    return jwt.encode(payload, config.JWT_SEGREDO, algorithm=config.JWT_ALGORITMO)


def autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer),
):
    if credenciais is None:
        raise HTTPException(401, "Token ausente.")
    try:
        return jwt.decode(
            credenciais.credentials,
            config.JWT_SEGREDO,
            algorithms=[config.JWT_ALGORITMO],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token invalido.")


def exige_operador(token=Depends(autenticado)):
    if token["tipo"] != "operador":
        raise HTTPException(403, "Apenas o operador da agencia pode executar esta operacao.")
    return token


def exige_servico(token=Depends(autenticado)):
    if token["tipo"] != "servico":
        raise HTTPException(403, "Esta rota so aceita chamadas entre agencias.")
    return token


def exige_dono(token, id_conta):
    """Autorizacao: cliente so opera a propria conta; operador opera qualquer uma."""
    if token["tipo"] == "operador":
        return
    if token["tipo"] != "cliente" or int(token["sub"]) != id_conta:
        raise HTTPException(403, "Voce so pode operar a sua propria conta.")
