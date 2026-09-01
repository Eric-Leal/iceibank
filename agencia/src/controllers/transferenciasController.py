import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

import config
from services import auth

router = APIRouter()


class Transferencia(BaseModel):
    idOrigem: int
    idDestino: int
    valor: float


class CreditoRemoto(BaseModel):
    valor: float
    timestampLamport: int
    origemAgencia: int


@router.post("/transferencias")
def transferir(dados: Transferencia, request: Request, token=Depends(auth.autenticado)):
    auth.exige_dono(token, dados.idOrigem)

    estado = request.app.state

    conta_origem = estado.contas.get(dados.idOrigem)
    if not conta_origem:
        raise HTTPException(404, "Conta de origem nao encontrada nesta agencia.")
    if conta_origem["saldo"] < dados.valor:
        raise HTTPException(400, "Saldo insuficiente.")

    agencia_destino = config.agencia_responsavel(dados.idDestino)

    # O debito e sempre local, pois esta agencia e a dona da conta de origem
    ts_debito = estado.relogio.evento_local()
    conta_origem["saldo"] -= dados.valor
    estado.registro.registrar(
        "TRANSFERENCIA_DEBITO",
        ts_debito,
        {"idOrigem": dados.idOrigem, "idDestino": dados.idDestino, "valor": dados.valor},
    )

    if agencia_destino == estado.id_agencia:
        # Caso simples: mesma agencia, credita direto
        conta_destino = estado.contas.get(dados.idDestino)
        if not conta_destino:
            conta_origem["saldo"] += dados.valor
            raise HTTPException(404, "Conta de destino nao encontrada.")

        ts_credito = estado.relogio.evento_local()
        conta_destino["saldo"] += dados.valor
        estado.registro.registrar(
            "TRANSFERENCIA_CREDITO",
            ts_credito,
            {"idOrigem": dados.idOrigem, "idDestino": dados.idDestino, "valor": dados.valor},
        )
        return {"mensagem": "Transferencia concluida (mesma agencia)."}

    # Caso entre agencias: chama a agencia de destino diretamente via REST
    ts_envio = estado.relogio.ao_enviar()
    url_destino = next(a["url"] for a in config.AGENCIAS if a["id"] == agencia_destino)

    # A chamada entre agencias leva um token de servico proprio, emitido por esta
    # agencia, em vez de repassar o token do cliente (ver justificativa em RESPOSTAS.md).
    token_servico = auth.gerar_token(sub=f"agencia-{estado.id_agencia}", tipo="servico", minutos=1)

    try:
        resposta = requests.post(
            f"{url_destino}/contas/{dados.idDestino}/creditar-remoto",
            json={
                "valor": dados.valor,
                "timestampLamport": ts_envio,
                "origemAgencia": estado.id_agencia,
            },
            headers={"Authorization": f"Bearer {token_servico}"},
            timeout=5,
        )
        resposta.raise_for_status()
        return {"mensagem": "Transferencia concluida (entre agencias)."}
    except requests.RequestException as erro:
        # LIMITACAO CONHECIDA: se esta chamada falhar, o debito ja aplicado acima
        # NAO e revertido - o dinheiro "desaparece" temporariamente. Resolver isso
        # de forma correta (garantir atomicidade mesmo sob falha) e o assunto do
        # Sprint 4, com uma transacao distribuida de verdade (2PC/Saga). Por
        # enquanto, so registramos a inconsistencia no log.
        estado.registro.registrar(
            "TRANSFERENCIA_FALHOU",
            estado.relogio.evento_local(),
            {
                "idOrigem": dados.idOrigem,
                "idDestino": dados.idDestino,
                "valor": dados.valor,
                "erro": str(erro),
            },
        )
        raise HTTPException(
            502,
            "Falha ao contatar agencia de destino. Debito ja aplicado - inconsistencia conhecida (ver Sprint 4).",
        )


@router.post("/contas/{id_conta}/creditar-remoto")
def creditar_remoto(
    id_conta: int, dados: CreditoRemoto, request: Request, token=Depends(auth.exige_servico)
):
    estado = request.app.state

    # Ao RECEBER uma mensagem de outra agencia, o relogio de Lamport e
    # atualizado com base no timestamp recebido - e a regra 3 do algoritmo.
    ts = estado.relogio.ao_receber(dados.timestampLamport)

    conta = estado.contas.get(id_conta)
    if not conta:
        raise HTTPException(404, "Conta nao encontrada nesta agencia.")

    conta["saldo"] += dados.valor
    estado.registro.registrar(
        "TRANSFERENCIA_CREDITO_REMOTO",
        ts,
        {"idConta": id_conta, "valor": dados.valor, "origemAgencia": dados.origemAgencia},
    )

    return {"mensagem": "Credito remoto aplicado.", "saldoAtual": conta["saldo"]}
