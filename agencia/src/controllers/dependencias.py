"""Dependencias da camada HTTP: autenticacao/autorizacao e acesso aos services."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services import auth

esquema_bearer = HTTPBearer(auto_error=False)


def autenticado(credenciais: HTTPAuthorizationCredentials = Depends(esquema_bearer)):
    if credenciais is None:
        raise HTTPException(401, "Token ausente.")
    return auth.decodificar_token(credenciais.credentials)


def exige_operador(token=Depends(autenticado)):
    if token["tipo"] != "operador":
        raise HTTPException(403, "Apenas o operador da agencia pode executar esta operacao.")
    return token


def exige_dono(token, id_conta):
    """Autorizacao: cliente so opera a propria conta; operador opera qualquer uma."""
    if token["tipo"] == "operador":
        return
    if token["tipo"] != "cliente" or int(token["sub"]) != id_conta:
        raise HTTPException(403, "Voce so pode operar a sua propria conta.")


def auth_service(request: Request):
    return request.app.state.auth_service


def contas_service(request: Request):
    return request.app.state.contas_service


def transferencias_service(request: Request):
    return request.app.state.transferencias_service
