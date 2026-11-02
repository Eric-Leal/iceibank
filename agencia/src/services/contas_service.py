import config
from models.conta import Conta
from services import auth
from services.comparar_vetores import comparar_vetores
from services.erros import (
    ConflitoSincronizacao,
    ContaDeOutraAgencia,
    ContaJaExiste,
    ContaNaoEncontrada,
    OperacaoNaoSuportada,
)


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

    def vetor_atual(self):
        return self.relogio.obter_vetor_atual()

    def sincronizar(self, id_conta, tipo, valor, vetor_conhecido):
        conta = self.consultar(id_conta)

        vetor_atual = self.relogio.obter_vetor_atual()
        if comparar_vetores(vetor_conhecido, vetor_atual) != "IGUAIS":
            # algo aconteceu na agencia desde a ultima leitura do app: nao aplica as cegas
            raise ConflitoSincronizacao(
                "Conflito detectado: o estado da conta mudou desde a ultima sincronizacao do app.",
                {
                    "vetorConhecido": vetor_conhecido,
                    "vetorAtual": vetor_atual,
                    "contaAtual": {"id": conta.id, "nomeAluno": conta.nome_aluno, "saldo": conta.saldo},
                },
            )

        if tipo == "DEPOSITO":
            conta.creditar(valor)
        elif tipo == "SAQUE":
            conta.debitar(valor)
        else:
            raise OperacaoNaoSuportada("Tipo de operacao pendente nao suportado.")

        ts = self.relogio.evento_local()
        self.contas.salvar(conta)
        self.registro.registrar(
            "SINCRONIZACAO_OFFLINE",
            ts,
            {"id": id_conta, "tipo": tipo, "valor": valor, "novoSaldo": conta.saldo},
        )
        return conta
