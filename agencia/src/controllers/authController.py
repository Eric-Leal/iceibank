from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

import config
from services import auth

router = APIRouter()


class LoginOperador(BaseModel):
    usuario: str
    senha: str


class LoginCliente(BaseModel):
    id: int
    senha: str


@router.post("/auth/login")
def login_cliente(dados: LoginCliente, request: Request):
    conta = request.app.state.contas.get(dados.id)
    if not conta or conta["senha"] != auth.hash_senha(dados.senha):
        raise HTTPException(401, "Credenciais invalidas.")

    return {
        "token": auth.gerar_token(sub=dados.id, tipo="cliente"),
        "tipo": "cliente",
        "expiraEmMinutos": config.JWT_EXPIRACAO_MINUTOS,
    }


@router.post("/auth/login-operador")
def login_operador(dados: LoginOperador):
    if dados.usuario != config.OPERADOR_USUARIO or dados.senha != config.OPERADOR_SENHA:
        raise HTTPException(401, "Credenciais invalidas.")

    return {
        "token": auth.gerar_token(sub=dados.usuario, tipo="operador"),
        "tipo": "operador",
        "expiraEmMinutos": config.JWT_EXPIRACAO_MINUTOS,
    }
