class TransferenciasRepository:
    """Transferencias ja aplicadas, para que nada seja aplicado duas vezes (idempotencia)."""

    def __init__(self):
        # Origem: resultado de cada transferencia, indexado pelo idOperacao
        self._aplicadas = {}
        # Destino: ids das mensagens de credito ja aplicadas
        self._creditos_recebidos = set()

    def buscar_resultado(self, id_operacao):
        return self._aplicadas.get(id_operacao)

    def registrar(self, id_operacao, resultado):
        self._aplicadas[id_operacao] = resultado

    def credito_ja_recebido(self, id_mensagem):
        return id_mensagem in self._creditos_recebidos

    def registrar_credito_recebido(self, id_mensagem):
        self._creditos_recebidos.add(id_mensagem)
