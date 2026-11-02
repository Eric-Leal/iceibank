import json
from pathlib import Path

pasta_dados = Path(__file__).parent / "data"

eventos = []
for arquivo in sorted(pasta_dados.glob("*.jsonl")):
    with open(arquivo, encoding="utf-8") as f:
        eventos.extend(json.loads(linha) for linha in f if linha.strip())

tipos_bully = {
    "ELEICAO_INICIADA",
    "ELEICAO_RECEBIDA",
    "TORNOU_LIDER",
    "LIDER_ANUNCIADO",
    "LIDER_NAO_RESPONDEU",
}
eventos_bully = sorted(
    (e for e in eventos if e["tipo"] in tipos_bully), key=lambda e: e["horaParede"]
)

print("=== Historico de eventos de eleicao ===")
for evento in eventos_bully:
    detalhes = json.dumps(evento["detalhes"], ensure_ascii=False)
    print(f"({evento['horaParede']}) [{evento['agencia']}] {evento['tipo']} {detalhes}")

print("\n=== Linha do tempo de lideres ===")
for evento in eventos_bully:
    if evento["tipo"] == "TORNOU_LIDER":
        print(f"A partir de {evento['horaParede']}: Agencia {evento['detalhes']['idAgencia']} e a lider")
