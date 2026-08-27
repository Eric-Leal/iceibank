import os
import sys

from fastapi import FastAPI

import config
from controllers.contasController import router as contas_router
from services.registro_eventos import RegistroEventos
from services.relogio_lamport import RelogioLamport

id_agencia = int(os.getenv("AGENCIA_ID", "0"))
agencia_config = next((a for a in config.AGENCIAS if a["id"] == id_agencia), None)

if agencia_config is None:
    print(f"Agencia {id_agencia} nao configurada em config.py")
    sys.exit(1)

app = FastAPI(title=f"ICEIBank - Agencia {id_agencia}")

app.state.id_agencia = id_agencia
app.state.relogio = RelogioLamport()
app.state.registro = RegistroEventos(f"agencia-{id_agencia}")
app.state.contas = {}

app.include_router(contas_router)


if __name__ == "__main__":
    import uvicorn

    porta = int(agencia_config["url"].rsplit(":", 1)[1])
    print(f"[Agencia {id_agencia}] ouvindo na porta {porta}")
    uvicorn.run(app, host="0.0.0.0", port=porta, log_level="warning")
