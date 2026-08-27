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
