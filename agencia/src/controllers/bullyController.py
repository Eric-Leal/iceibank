from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class MensagemEleicao(BaseModel):
    origemId: int
    vetorEnvio: list[int]


class MensagemCoordenador(BaseModel):
    liderId: int
    vetorEnvio: list[int]


@router.post("/bully/eleicao")
async def eleicao(dados: MensagemEleicao, request: Request):
    request.app.state.bully.receber_eleicao(dados.origemId, dados.vetorEnvio)
    return {"ok": True}


@router.post("/bully/coordenador")
async def coordenador(dados: MensagemCoordenador, request: Request):
    request.app.state.bully.receber_coordenador(dados.liderId, dados.vetorEnvio)
    return {"ok": True}


@router.get("/bully/lider")
async def lider(request: Request):
    bully = request.app.state.bully
    return {"idAgencia": bully.id_agencia, "liderAtual": bully.obter_lider_atual()}
