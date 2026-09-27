from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

import config
from services import auth, mensageria

router = APIRouter()


class Transferencia(BaseModel):
    idOrigem: int
    idDestino: int
    valor: float
    idOperacao: str | None = None


def registrar_conclusao(estado, id_operacao, resposta):
    if id_operacao:
        estado.transferencias_aplicadas[id_operacao] = resposta
    return resposta


@router.post("/transferencias")
async def transferir(dados: Transferencia, request: Request, token=Depends(auth.autenticado)):
    auth.exige_dono(token, dados.idOrigem)

    estado = request.app.state

    # Idempotencia: a mesma operacao reenviada nao pode debitar duas vezes.
    if dados.idOperacao and dados.idOperacao in estado.transferencias_aplicadas:
        estado.registro.registrar(
            "TRANSFERENCIA_IGNORADA",
            estado.relogio.evento_local(),
            {
                "idOperacao": dados.idOperacao,
                "idOrigem": dados.idOrigem,
                "idDestino": dados.idDestino,
                "valor": dados.valor,
            },
        )
        return estado.transferencias_aplicadas[dados.idOperacao]

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
        return registrar_conclusao(
            estado, dados.idOperacao, {"mensagem": "Transferencia concluida (mesma agencia)."}
        )

    # Em vez de chamar a outra agencia diretamente (Sprint 1), publicamos um
    # evento na exchange do RabbitMQ. A agencia de destino consome quando
    # estiver disponivel - mesmo que esteja fora do ar agora, a mensagem fica
    # retida na fila (durable) e e entregue quando ela voltar.
    vetor_envio = estado.relogio.ao_enviar()
    await mensageria.publicar(
        f"agencia.{agencia_destino}.creditar",
        {
            "idConta": dados.idDestino,
            "valor": dados.valor,
            "vetorEnvio": vetor_envio,
            "origemAgencia": estado.id_agencia,
        },
    )

    return registrar_conclusao(
        estado,
        dados.idOperacao,
        {"mensagem": "Transferencia publicada para a agencia de destino (entrega assincrona)."},
    )


def processar_credito_remoto(estado, mensagem):
    """Consumidor da fila desta agencia: aplica creditos vindos de outras agencias."""
    # Ao RECEBER uma mensagem de outra agencia, o relogio vetorial e
    # atualizado com base no vetor recebido - e a regra 3 do algoritmo.
    vetor = estado.relogio.ao_receber(mensagem["vetorEnvio"])

    detalhes = {
        "idConta": mensagem["idConta"],
        "valor": mensagem["valor"],
        "origemAgencia": mensagem["origemAgencia"],
    }

    conta = estado.contas.get(mensagem["idConta"])
    if not conta:
        estado.registro.registrar(
            "CREDITO_REMOTO_FALHOU", vetor, {**detalhes, "motivo": "conta nao encontrada"}
        )
        return

    conta["saldo"] += mensagem["valor"]
    estado.registro.registrar("TRANSFERENCIA_CREDITO_REMOTO", vetor, detalhes)
