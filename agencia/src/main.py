import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from controllers.authController import router as auth_router
from controllers.contasController import router as contas_router
from controllers.transferenciasController import processar_credito_remoto
from controllers.transferenciasController import router as transferencias_router
from services import mensageria
from services.registro_eventos import RegistroEventos
from services.relogio_vetorial import RelogioVetorial

id_agencia = int(os.getenv("AGENCIA_ID", "0"))
agencia_config = next((a for a in config.AGENCIAS if a["id"] == id_agencia), None)

if agencia_config is None:
    print(f"Agencia {id_agencia} nao configurada em config.py")
    sys.exit(1)

@asynccontextmanager
async def lifespan(app):
    # Consumidor: processa creditos vindos de outras agencias via RabbitMQ
    await mensageria.assinar(id_agencia, lambda mensagem: processar_credito_remoto(app.state, mensagem))
    yield


app = FastAPI(title=f"ICEIBank - Agencia {id_agencia}", lifespan=lifespan)

# O frontend roda em outra porta, entao o navegador precisa da liberacao explicita.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENS_FRONTEND,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.id_agencia = id_agencia
app.state.relogio = RelogioVetorial(id_agencia, config.NUMERO_AGENCIAS)
app.state.registro = RegistroEventos(f"agencia-{id_agencia}")
app.state.contas = {}
# Resultado das transferencias ja aplicadas, indexado pelo idOperacao (idempotencia).
app.state.transferencias_aplicadas = {}

app.include_router(auth_router)
app.include_router(contas_router)
app.include_router(transferencias_router)


if __name__ == "__main__":
    import uvicorn

    porta = int(agencia_config["url"].rsplit(":", 1)[1])
    print(f"[Agencia {id_agencia}] ouvindo na porta {porta}")
    uvicorn.run(app, host="0.0.0.0", port=porta, log_level="warning")
