from fastapi import APIRouter, Depends
from pydantic import BaseModel

from controllers.dependencias import auth_service

router = APIRouter()


class LoginOperador(BaseModel):
    usuario: str
    senha: str


class LoginCliente(BaseModel):
    id: int
    senha: str


@router.post("/auth/login")
def login_cliente(dados: LoginCliente, servico=Depends(auth_service)):
    return servico.login_cliente(dados.id, dados.senha)


@router.post("/auth/login-operador")
def login_operador(dados: LoginOperador, servico=Depends(auth_service)):
    return servico.login_operador(dados.usuario, dados.senha)
