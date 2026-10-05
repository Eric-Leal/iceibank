"""Testa a mensageria fora da aplicacao: cada fila so recebe a propria routing key."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from services import mensageria  # noqa: E402

AGENCIAS = [0, 1, 2]


async def main():
    recebidas = {id_agencia: [] for id_agencia in AGENCIAS}
    todas_chegaram = asyncio.Event()

    def registrar_em(id_agencia):
        def ao_receber(conteudo):
            print(f"fila-agencia-{id_agencia} recebeu {conteudo}")
            recebidas[id_agencia].append(conteudo)
            if all(recebidas.values()):
                todas_chegaram.set()

        return ao_receber

    for id_agencia in AGENCIAS:
        await mensageria.assinar(id_agencia, registrar_em(id_agencia))

    for id_agencia in AGENCIAS:
        routing_key = f"agencia.{id_agencia}.creditar"
        print(f"publicando em {routing_key}")
        await mensageria.publicar(routing_key, {"teste": id_agencia})

    await asyncio.wait_for(todas_chegaram.wait(), timeout=10)

    for id_agencia in AGENCIAS:
        assert recebidas[id_agencia] == [{"teste": id_agencia}], recebidas
    print("mensageria OK: cada fila recebeu so a propria mensagem")


asyncio.run(main())
