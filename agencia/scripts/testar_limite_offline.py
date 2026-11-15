"""Checa o limite de saque offline no service, sem precisar das agencias no ar.

Uso (de dentro de agencia/): python scripts/testar_limite_offline.py
"""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import config  # noqa: E402
from repositories.contas_repository import ContasRepository  # noqa: E402
from services.contas_service import ContasService  # noqa: E402
from services.erros import LimiteOfflineExcedido  # noqa: E402
from services.relogio_vetorial import RelogioVetorial  # noqa: E402

servico = ContasService(0, ContasRepository(), RelogioVetorial(0, 3), MagicMock())
servico.criar(3, "Teste", "senha", 1000)

try:
    servico.sincronizar(3, "SAQUE", config.LIMITE_SAQUE_OFFLINE + 1, servico.vetor_atual())
    raise AssertionError("saque acima do limite foi aceito")
except LimiteOfflineExcedido:
    pass

assert servico.sincronizar(3, "SAQUE", config.LIMITE_SAQUE_OFFLINE, servico.vetor_atual()).saldo == 800
assert servico.sincronizar(3, "DEPOSITO", 5000, servico.vetor_atual()).saldo == 5800
print("limite offline OK")
