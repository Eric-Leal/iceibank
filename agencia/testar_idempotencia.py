"""Simula o RabbitMQ entregando a mesma mensagem de credito duas vezes.

Uso (com as agencias no ar): python testar_idempotencia.py <conta destino> <valor>
A agencia dona da conta deve creditar uma vez e registrar CREDITO_REMOTO_IGNORADO na segunda.
"""

import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import config  # noqa: E402
from services import mensageria  # noqa: E402


async def main():
    id_conta = int(sys.argv[1])
    valor = float(sys.argv[2])
    agencia_destino = config.agencia_responsavel(id_conta)

    mensagem = {
        "idMensagem": str(uuid.uuid4()),
        "idConta": id_conta,
        "valor": valor,
        "vetorEnvio": [0] * config.NUMERO_AGENCIAS,
        "origemAgencia": "teste",
    }
    for entrega in (1, 2):
        await mensageria.publicar(f"agencia.{agencia_destino}.creditar", mensagem)
        print(f"entrega {entrega}: {mensagem}")


asyncio.run(main())
