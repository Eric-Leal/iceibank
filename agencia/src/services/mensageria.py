import json
import os
import sys

import aio_pika

import config  # noqa: F401  (carrega o agencia/.env antes de ler RABBITMQ_URL)

URL_RABBITMQ = os.getenv("RABBITMQ_URL")
EXCHANGE = "iceibank.eventos"

if not URL_RABBITMQ:
    print("Defina RABBITMQ_URL (no agencia/.env ou no terminal) com a URL AMQP da sua instancia CloudAMQP.")
    sys.exit(1)

_canal = None
_exchange = None


async def _obter_canal():
    global _canal, _exchange
    if _canal:
        return _canal, _exchange
    # connect_robust reconecta sozinho se a conexao com o broker cair
    conexao = await aio_pika.connect_robust(URL_RABBITMQ)
    _canal = await conexao.channel()
    _exchange = await _canal.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)
    return _canal, _exchange


async def publicar(routing_key, mensagem):
    _, exchange = await _obter_canal()
    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(mensagem).encode("utf-8"),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=routing_key,
    )


async def assinar(id_agencia, ao_receber_mensagem):
    canal, exchange = await _obter_canal()
    fila = await canal.declare_queue(f"fila-agencia-{id_agencia}", durable=True)
    await fila.bind(exchange, routing_key=f"agencia.{id_agencia}.creditar")

    async def ao_chegar(mensagem):
        conteudo = json.loads(mensagem.body)
        ao_receber_mensagem(conteudo)
        await mensagem.ack()

    await fila.consume(ao_chegar)
