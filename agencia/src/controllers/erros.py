from fastapi.responses import JSONResponse

from services.erros import (
    ContaDeOutraAgencia,
    ContaJaExiste,
    ContaNaoEncontrada,
    CredenciaisInvalidas,
    ErroNegocio,
    SaldoInsuficiente,
    TokenInvalido,
)

# Traducao de erro de negocio para status HTTP; o service nao conhece HTTP.
STATUS_POR_ERRO = {
    ContaNaoEncontrada: 404,
    ContaJaExiste: 409,
    ContaDeOutraAgencia: 400,
    SaldoInsuficiente: 400,
    CredenciaisInvalidas: 401,
    TokenInvalido: 401,
}


async def tratar_erro_negocio(request, erro: ErroNegocio):
    status = STATUS_POR_ERRO.get(type(erro), 400)
    return JSONResponse(status_code=status, content={"detail": str(erro)})
