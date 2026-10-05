from dataclasses import dataclass

from services.erros import SaldoInsuficiente


@dataclass
class Conta:
    id: int
    nome_aluno: str
    saldo: float
    senha_hash: str

    def creditar(self, valor):
        self.saldo += valor

    def debitar(self, valor):
        if self.saldo < valor:
            raise SaldoInsuficiente("Saldo insuficiente.")
        self.saldo -= valor
