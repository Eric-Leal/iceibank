import json
from pathlib import Path

pasta_dados = Path(__file__).parent / "data"

todos_eventos = []
for arquivo in sorted(pasta_dados.glob("*.jsonl")):
    with open(arquivo, encoding="utf-8") as f:
        todos_eventos.extend(json.loads(linha) for linha in f if linha.strip())

todos_eventos.sort(key=lambda e: e["timestampLamport"])

print("=== Linha do tempo unificada (ordenada por relogio de Lamport) ===")
for evento in todos_eventos:
    detalhes = json.dumps(evento["detalhes"], ensure_ascii=False)
    print(
        f"[Lamport {evento['timestampLamport']}] ({evento['horaParede']}) "
        f"{evento['agencia']} - {evento['tipo']} {detalhes}"
    )
