import config
from services.erros import ContaNaoEncontrada


class TransferenciasService:
    def __init__(self, id_agencia, contas, transferencias, relogio, registro, mensageria):
        self.id_agencia = id_agencia
        self.contas = contas
        self.transferencias = transferencias
        self.relogio = relogio
        self.registro = registro
        self.mensageria = mensageria

    async def transferir(self, id_origem, id_destino, valor, id_operacao=None):
        detalhes = {"idOrigem": id_origem, "idDestino": id_destino, "valor": valor}

        # Idempotencia: a mesma operacao reenviada nao pode debitar duas vezes.
        if id_operacao:
            resultado = self.transferencias.buscar_resultado(id_operacao)
            if resultado:
                self.registro.registrar(
                    "TRANSFERENCIA_IGNORADA",
                    self.relogio.evento_local(),
                    {"idOperacao": id_operacao, **detalhes},
                )
                return resultado

        conta_origem = self.contas.buscar(id_origem)
        if not conta_origem:
            raise ContaNaoEncontrada("Conta de origem nao encontrada nesta agencia.")

        # O debito e sempre local, pois esta agencia e a dona da conta de origem
        conta_origem.debitar(valor)
        ts_debito = self.relogio.evento_local()
        self.contas.salvar(conta_origem)
        self.registro.registrar("TRANSFERENCIA_DEBITO", ts_debito, detalhes)

        agencia_destino = config.agencia_responsavel(id_destino)
        if agencia_destino == self.id_agencia:
            # Caso simples: mesma agencia, credita direto
            conta_destino = self.contas.buscar(id_destino)
            if not conta_destino:
                conta_origem.creditar(valor)
                self.contas.salvar(conta_origem)
                raise ContaNaoEncontrada("Conta de destino nao encontrada.")

            ts_credito = self.relogio.evento_local()
            conta_destino.creditar(valor)
            self.contas.salvar(conta_destino)
            self.registro.registrar("TRANSFERENCIA_CREDITO", ts_credito, detalhes)
            return self._concluir(id_operacao, "Transferencia concluida (mesma agencia).")

        # Em vez de chamar a outra agencia diretamente (Sprint 1), publicamos um
        # evento na exchange do RabbitMQ. A agencia de destino consome quando
        # estiver disponivel - mesmo que esteja fora do ar agora, a mensagem fica
        # retida na fila (durable) e e entregue quando ela voltar.
        vetor_envio = self.relogio.ao_enviar()
        await self.mensageria.publicar(
            f"agencia.{agencia_destino}.creditar",
            {
                "idConta": id_destino,
                "valor": valor,
                "vetorEnvio": vetor_envio,
                "origemAgencia": self.id_agencia,
            },
        )
        return self._concluir(
            id_operacao, "Transferencia publicada para a agencia de destino (entrega assincrona)."
        )

    def processar_credito_remoto(self, mensagem):
        """Consumidor da fila desta agencia: aplica creditos vindos de outras agencias."""
        # Ao RECEBER uma mensagem de outra agencia, o relogio vetorial e
        # atualizado com base no vetor recebido - e a regra 3 do algoritmo.
        vetor = self.relogio.ao_receber(mensagem["vetorEnvio"])

        detalhes = {
            "idConta": mensagem["idConta"],
            "valor": mensagem["valor"],
            "origemAgencia": mensagem["origemAgencia"],
        }

        conta = self.contas.buscar(mensagem["idConta"])
        if not conta:
            self.registro.registrar(
                "CREDITO_REMOTO_FALHOU", vetor, {**detalhes, "motivo": "conta nao encontrada"}
            )
            return

        conta.creditar(mensagem["valor"])
        self.contas.salvar(conta)
        self.registro.registrar("TRANSFERENCIA_CREDITO_REMOTO", vetor, detalhes)

    def _concluir(self, id_operacao, mensagem):
        resultado = {"mensagem": mensagem}
        if id_operacao:
            self.transferencias.registrar(id_operacao, resultado)
        return resultado
