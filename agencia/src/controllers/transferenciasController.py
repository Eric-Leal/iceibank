from fastapi import APIRouter, Depends
from pydantic import BaseModel

from controllers.dependencias import autenticado, exige_dono, transferencias_service

router = APIRouter()


class Transferencia(BaseModel):
    idOrigem: int
    idDestino: int
    valor: float
    idOperacao: str | None = None


@router.post("/transferencias")
async def transferir(
    dados: Transferencia, token=Depends(autenticado), servico=Depends(transferencias_service)
):
    exige_dono(token, dados.idOrigem)
    return await servico.transferir(dados.idOrigem, dados.idDestino, dados.valor, dados.idOperacao)
