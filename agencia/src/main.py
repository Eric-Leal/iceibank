import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from controllers.authController import router as auth_router
from controllers.contasController import router as contas_router
from controllers.erros import tratar_erro_negocio
from controllers.transferenciasController import router as transferencias_router
from repositories.contas_repository import ContasRepository
from repositories.transferencias_repository import TransferenciasRepository
from services import mensageria
from services.auth import AuthService
from services.contas_service import ContasService
from services.erros import ErroNegocio
from services.registro_eventos import RegistroEventos
from services.relogio_vetorial import RelogioVetorial
from services.transferencias_service import TransferenciasService

id_agencia = int(os.getenv("AGENCIA_ID", "0"))
agencia_config = next((a for a in config.AGENCIAS if a["id"] == id_agencia), None)

if agencia_config is None:
    print(f"Agencia {id_agencia} nao configurada em config.py")
    sys.exit(1)

# Montagem das camadas: repositories (dados) -> services (regras) -> controllers (HTTP)
contas = ContasRepository()
transferencias = TransferenciasRepository()
relogio = RelogioVetorial(id_agencia, config.NUMERO_AGENCIAS)
registro = RegistroEventos(f"agencia-{id_agencia}")

auth_service = AuthService(contas)
contas_service = ContasService(id_agencia, contas, relogio, registro)
transferencias_service = TransferenciasService(
    id_agencia, contas, transferencias, relogio, registro, mensageria
)


@asynccontextmanager
async def lifespan(app):
    # Consumidor: processa creditos vindos de outras agencias via RabbitMQ
    await mensageria.assinar(id_agencia, transferencias_service.processar_credito_remoto)
    yield


app = FastAPI(title=f"ICEIBank - Agencia {id_agencia}", lifespan=lifespan)
app.add_exception_handler(ErroNegocio, tratar_erro_negocio)

# O frontend roda em outra porta, entao o navegador precisa da liberacao explicita.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENS_FRONTEND,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.auth_service = auth_service
app.state.contas_service = contas_service
app.state.transferencias_service = transferencias_service

app.include_router(auth_router)
app.include_router(contas_router)
app.include_router(transferencias_router)


if __name__ == "__main__":
    import uvicorn

    porta = int(agencia_config["url"].rsplit(":", 1)[1])
    print(f"[Agencia {id_agencia}] ouvindo na porta {porta}")
    uvicorn.run(app, host="0.0.0.0", port=porta, log_level="warning")
