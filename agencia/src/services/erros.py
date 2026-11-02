"""Erros de regra de negocio. Os services levantam; o controller traduz para HTTP."""


class ErroNegocio(Exception):
    pass


class ContaNaoEncontrada(ErroNegocio):
    pass


class ContaJaExiste(ErroNegocio):
    pass


class ContaDeOutraAgencia(ErroNegocio):
    pass


class SaldoInsuficiente(ErroNegocio):
    pass


class CredenciaisInvalidas(ErroNegocio):
    pass


class TokenInvalido(ErroNegocio):
    pass


class OperacaoNaoSuportada(ErroNegocio):
    pass


class ConflitoSincronizacao(ErroNegocio):
    def __init__(self, mensagem, dados):
        super().__init__(mensagem)
        self.dados = dados
