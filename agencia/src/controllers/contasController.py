from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

import config
from services import auth

router = APIRouter()


class NovaConta(BaseModel):
    id: int
    nomeAluno: str
    senha: str
    saldoInicial: float = 0


class Valor(BaseModel):
    valor: float


def sem_senha(conta):
    return {k: v for k, v in conta.items() if k != "senha"}


@router.post("/contas", status_code=201)
def criar_conta(dados: NovaConta, request: Request, token=Depends(auth.exige_operador)):
    estado = request.app.state

    if config.agencia_responsavel(dados.id) != estado.id_agencia:
        raise HTTPException(400, f"Conta {dados.id} nao pertence a esta agencia.")
    if dados.id in estado.contas:
        raise HTTPException(409, "Conta ja existe.")

    ts = estado.relogio.evento_local()
    estado.contas[dados.id] = {
        "id": dados.id,
        "nomeAluno": dados.nomeAluno,
        "saldo": dados.saldoInicial,
        "senha": auth.hash_senha(dados.senha),
    }
    estado.registro.registrar(
        "CRIAR_CONTA",
        ts,
        {"id": dados.id, "nomeAluno": dados.nomeAluno, "saldoInicial": dados.saldoInicial},
    )

    return sem_senha(estado.contas[dados.id])


@router.get("/contas/{id_conta}")
def consultar_saldo(id_conta: int, request: Request, token=Depends(auth.autenticado)):
    auth.exige_dono(token, id_conta)

    conta = request.app.state.contas.get(id_conta)
    if not conta:
        raise HTTPException(404, "Conta nao encontrada nesta agencia.")
    return sem_senha(conta)


@router.post("/contas/{id_conta}/depositar")
def depositar(id_conta: int, dados: Valor, request: Request, token=Depends(auth.autenticado)):
    auth.exige_dono(token, id_conta)

    estado = request.app.state
    conta = estado.contas.get(id_conta)
    if not conta:
        raise HTTPException(404, "Conta nao encontrada nesta agencia.")

    ts = estado.relogio.evento_local()
    conta["saldo"] += dados.valor
    estado.registro.registrar(
        "DEPOSITO", ts, {"id": id_conta, "valor": dados.valor, "novoSaldo": conta["saldo"]}
    )

    return sem_senha(conta)


@router.post("/contas/{id_conta}/sacar")
def sacar(id_conta: int, dados: Valor, request: Request, token=Depends(auth.autenticado)):
    auth.exige_dono(token, id_conta)

    estado = request.app.state
    conta = estado.contas.get(id_conta)
    if not conta:
        raise HTTPException(404, "Conta nao encontrada nesta agencia.")
    if conta["saldo"] < dados.valor:
        raise HTTPException(400, "Saldo insuficiente.")

    ts = estado.relogio.evento_local()
    conta["saldo"] -= dados.valor
    estado.registro.registrar(
        "SAQUE", ts, {"id": id_conta, "valor": dados.valor, "novoSaldo": conta["saldo"]}
    )

    return sem_senha(conta)
