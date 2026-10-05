class ContasRepository:
    """Acesso aos dados das contas. Hoje em memoria; trocar o armazenamento mexe so aqui."""

    def __init__(self):
        self._contas = {}

    def buscar(self, id_conta):
        return self._contas.get(id_conta)

    def existe(self, id_conta):
        return id_conta in self._contas

    def salvar(self, conta):
        self._contas[conta.id] = conta
