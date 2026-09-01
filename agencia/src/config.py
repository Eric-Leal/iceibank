import os

# OFFSET pessoal (dois ultimos digitos da matricula/RA)
OFFSET = 81

NUMERO_AGENCIAS = 3
PORTA_BASE = 8000 + OFFSET

AGENCIAS = [
    {"id": 0, "url": f"http://localhost:{PORTA_BASE}"},
    {"id": 1, "url": f"http://localhost:{PORTA_BASE + 1}"},
    {"id": 2, "url": f"http://localhost:{PORTA_BASE + 2}"},
]


def agencia_responsavel(id_conta):
    return id_conta % NUMERO_AGENCIAS


# Autenticacao (Parte F)
# A chave e lida do ambiente; o valor abaixo e so um padrao de desenvolvimento.
JWT_SEGREDO = os.getenv("JWT_SEGREDO", "iceibank-sprint1-segredo-de-desenvolvimento")
JWT_ALGORITMO = "HS256"
JWT_EXPIRACAO_MINUTOS = 30

# Credencial fixa do operador da agencia, unica capaz de criar contas novas.
OPERADOR_USUARIO = "operador"
OPERADOR_SENHA = "iceibank123"
