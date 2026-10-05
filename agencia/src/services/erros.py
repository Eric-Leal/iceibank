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
