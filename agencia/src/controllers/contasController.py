from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from controllers.dependencias import autenticado, contas_service, exige_dono, exige_operador

router = APIRouter()


class NovaConta(BaseModel):
    id: int
    nomeAluno: str
    senha: str
    saldoInicial: float = 0


class Valor(BaseModel):
    valor: float


class ContaResposta(BaseModel):
    """O que a API devolve de uma conta: nunca inclui a senha."""

    id: int
    nomeAluno: str
    saldo: float
    vetorAtual: list[int] | None = None


class OperacaoPendente(BaseModel):
    tipo: Literal["DEPOSITO", "SAQUE"]
    valor: float = Field(gt=0)
    vetorConhecido: list[int]


def para_resposta(conta, vetor_atual=None):
    return ContaResposta(
        id=conta.id, nomeAluno=conta.nome_aluno, saldo=conta.saldo, vetorAtual=vetor_atual
    )


@router.post("/contas", status_code=201, response_model=ContaResposta)
def criar_conta(dados: NovaConta, token=Depends(exige_operador), servico=Depends(contas_service)):
    conta = servico.criar(dados.id, dados.nomeAluno, dados.senha, dados.saldoInicial)
    return para_resposta(conta)


@router.get("/contas/{id_conta}", response_model=ContaResposta)
def consultar_saldo(id_conta: int, token=Depends(autenticado), servico=Depends(contas_service)):
    exige_dono(token, id_conta)
    # O app offline-first guarda esse vetor e devolve na sincronizacao.
    return para_resposta(servico.consultar(id_conta), servico.vetor_atual())


@router.post("/contas/{id_conta}/depositar", response_model=ContaResposta)
def depositar(
    id_conta: int, dados: Valor, token=Depends(autenticado), servico=Depends(contas_service)
):
    exige_dono(token, id_conta)
    return para_resposta(servico.depositar(id_conta, dados.valor), servico.vetor_atual())


@router.post("/contas/{id_conta}/sacar", response_model=ContaResposta)
def sacar(id_conta: int, dados: Valor, token=Depends(autenticado), servico=Depends(contas_service)):
    exige_dono(token, id_conta)
    return para_resposta(servico.sacar(id_conta, dados.valor), servico.vetor_atual())


@router.post("/contas/{id_conta}/sincronizar", response_model=ContaResposta)
def sincronizar(
    id_conta: int,
    dados: OperacaoPendente,
    token=Depends(autenticado),
    servico=Depends(contas_service),
):
    exige_dono(token, id_conta)
    conta = servico.sincronizar(id_conta, dados.tipo, dados.valor, dados.vetorConhecido)
    return para_resposta(conta, servico.vetor_atual())
