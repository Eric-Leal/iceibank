import asyncio

import httpx

import config

TIMEOUT_S = 1.0


class ServicoBully:
    def __init__(self, id_agencia, relogio, registro):
        self.id_agencia = id_agencia
        self.relogio = relogio
        self.registro = registro
        self.lider_atual = None
        self.eleicao_em_andamento = False

    def _agencias_com_id_maior(self):
        return [a for a in config.AGENCIAS if a["id"] > self.id_agencia]

    async def iniciar_eleicao(self):
        if self.eleicao_em_andamento:
            return
        self.eleicao_em_andamento = True
        vetor = self.relogio.evento_local()
        self.registro.registrar("ELEICAO_INICIADA", vetor, {"idAgencia": self.id_agencia})

        alguem_respondeu = False
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as cliente:
            for agencia in self._agencias_com_id_maior():
                try:
                    vetor_envio = self.relogio.ao_enviar()
                    resposta = await cliente.post(
                        f"{agencia['url']}/bully/eleicao",
                        json={"origemId": self.id_agencia, "vetorEnvio": vetor_envio},
                    )
                    resposta.raise_for_status()
                    alguem_respondeu = True
                except httpx.HTTPError:
                    pass  # agencia fora do ar ou lenta demais: segue para a proxima

        self.eleicao_em_andamento = False

        # se alguem maior respondeu, ela conduz a eleicao e anuncia via /bully/coordenador
        if not alguem_respondeu:
            await self._tornar_me_lider()

    async def _tornar_me_lider(self):
        self.lider_atual = self.id_agencia
        vetor = self.relogio.evento_local()
        self.registro.registrar("TORNOU_LIDER", vetor, {"idAgencia": self.id_agencia})
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as cliente:
            for agencia in config.AGENCIAS:
                if agencia["id"] == self.id_agencia:
                    continue
                try:
                    vetor_envio = self.relogio.ao_enviar()
                    await cliente.post(
                        f"{agencia['url']}/bully/coordenador",
                        json={"liderId": self.id_agencia, "vetorEnvio": vetor_envio},
                    )
                except httpx.HTTPError:
                    pass  # descobre a lider quando voltar

    def receber_eleicao(self, origem_id, vetor_recebido):
        vetor = self.relogio.ao_receber(vetor_recebido)
        self.registro.registrar(
            "ELEICAO_RECEBIDA", vetor, {"de": origem_id, "minhaId": self.id_agencia}
        )
        # roda em segundo plano para o 200 voltar antes do timeout de quem perguntou
        asyncio.create_task(self.iniciar_eleicao())

    def receber_coordenador(self, lider_id, vetor_recebido):
        self.lider_atual = lider_id
        vetor = self.relogio.ao_receber(vetor_recebido)
        self.registro.registrar(
            "LIDER_ANUNCIADO", vetor, {"liderId": lider_id, "agencia": self.id_agencia}
        )

    def obter_lider_atual(self):
        return self.lider_atual

    async def verificar_lider(self):
        if self.lider_atual is None:
            await self.iniciar_eleicao()
            return
        if self.lider_atual == self.id_agencia:
            return

        lider_info = next(a for a in config.AGENCIAS if a["id"] == self.lider_atual)
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_S) as cliente:
                resposta = await cliente.get(f"{lider_info['url']}/bully/lider")
                resposta.raise_for_status()
        except httpx.HTTPError:
            vetor = self.relogio.evento_local()
            self.registro.registrar(
                "LIDER_NAO_RESPONDEU",
                vetor,
                {"liderAtual": self.lider_atual, "agencia": self.id_agencia},
            )
            self.lider_atual = None
            await self.iniciar_eleicao()

    async def iniciar_heartbeat(self, intervalo_s=3.0):
        while True:
            await asyncio.sleep(intervalo_s)
            await self.verificar_lider()
