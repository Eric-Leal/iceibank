import json
import os
from datetime import datetime, timezone


class RegistroEventos:
    def __init__(self, nome_agencia):
        self.nome_agencia = nome_agencia
        pasta_dados = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "data"
        )
        os.makedirs(pasta_dados, exist_ok=True)
        self.caminho_arquivo = os.path.join(pasta_dados, f"eventos-{nome_agencia}.jsonl")

    def registrar(self, tipo, timestamp_vetorial, detalhes):
        evento = {
            "agencia": self.nome_agencia,
            "tipo": tipo,
            "timestampVetorial": timestamp_vetorial,
            "horaParede": datetime.now(timezone.utc).isoformat(),
            "detalhes": detalhes,
        }
        with open(self.caminho_arquivo, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
        print(f"[Vetor {timestamp_vetorial}] {tipo} {detalhes}")
        return evento
