class TransferenciasRepository:
    """Resultado das transferencias ja aplicadas, indexado pelo idOperacao (idempotencia)."""

    def __init__(self):
        self._aplicadas = {}

    def buscar_resultado(self, id_operacao):
        return self._aplicadas.get(id_operacao)

    def registrar(self, id_operacao, resultado):
        self._aplicadas[id_operacao] = resultado
