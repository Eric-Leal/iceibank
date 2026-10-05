import config
from models.conta import Conta
from services import auth
from services.erros import ContaDeOutraAgencia, ContaJaExiste, ContaNaoEncontrada


class ContasService:
    def __init__(self, id_agencia, contas, relogio, registro):
        self.id_agencia = id_agencia
        self.contas = contas
        self.relogio = relogio
        self.registro = registro

    def criar(self, id_conta, nome_aluno, senha, saldo_inicial):
        if config.agencia_responsavel(id_conta) != self.id_agencia:
            raise ContaDeOutraAgencia(f"Conta {id_conta} nao pertence a esta agencia.")
        if self.contas.existe(id_conta):
            raise ContaJaExiste("Conta ja existe.")

        ts = self.relogio.evento_local()
        conta = Conta(id_conta, nome_aluno, saldo_inicial, auth.hash_senha(senha))
        self.contas.salvar(conta)
        self.registro.registrar(
            "CRIAR_CONTA",
            ts,
            {"id": id_conta, "nomeAluno": nome_aluno, "saldoInicial": saldo_inicial},
        )
        return conta

    def consultar(self, id_conta):
        conta = self.contas.buscar(id_conta)
        if not conta:
            raise ContaNaoEncontrada("Conta nao encontrada nesta agencia.")
        return conta

    def depositar(self, id_conta, valor):
        conta = self.consultar(id_conta)

        ts = self.relogio.evento_local()
        conta.creditar(valor)
        self.contas.salvar(conta)
        self.registro.registrar(
            "DEPOSITO", ts, {"id": id_conta, "valor": valor, "novoSaldo": conta.saldo}
        )
        return conta

    def sacar(self, id_conta, valor):
        conta = self.consultar(id_conta)

        conta.debitar(valor)
        ts = self.relogio.evento_local()
        self.contas.salvar(conta)
        self.registro.registrar(
            "SAQUE", ts, {"id": id_conta, "valor": valor, "novoSaldo": conta.saldo}
        )
        return conta
