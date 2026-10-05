import json
from pathlib import Path

pasta_dados = Path(__file__).parent / "data"

todos_eventos = []
for arquivo in sorted(pasta_dados.glob("*.jsonl")):
    with open(arquivo, encoding="utf-8") as f:
        todos_eventos.extend(json.loads(linha) for linha in f if linha.strip())

todos_eventos.sort(key=lambda e: e["horaParede"])

print("=== Linha do tempo (ordenada por hora de parede) ===")
for evento in todos_eventos:
    detalhes = json.dumps(evento["detalhes"], ensure_ascii=False)
    print(f"[{evento['agencia']}] vetor={evento['timestampVetorial']} {evento['tipo']} {detalhes}")


def comparar_vetores(v1, v2):
    v1_menor_ou_igual = all(a <= b for a, b in zip(v1, v2))
    v2_menor_ou_igual = all(b <= a for a, b in zip(v1, v2))
    if v1_menor_ou_igual and v2_menor_ou_igual:
        return "IGUAIS"
    if v1_menor_ou_igual:
        return "ANTES"
    if v2_menor_ou_igual:
        return "DEPOIS"
    return "CONCORRENTES"


print("\n=== Pares de eventos CONCORRENTES entre agencias diferentes ===")
encontrou_concorrente = False
for i, e1 in enumerate(todos_eventos):
    for e2 in todos_eventos[i + 1 :]:
        if e1["agencia"] == e2["agencia"]:
            continue
        if comparar_vetores(e1["timestampVetorial"], e2["timestampVetorial"]) == "CONCORRENTES":
            encontrou_concorrente = True
            print(
                f"[{e1['agencia']}] {e1['tipo']} ({e1['timestampVetorial']})  x  "
                f"[{e2['agencia']}] {e2['tipo']} ({e2['timestampVetorial']})"
            )
if not encontrou_concorrente:
    print(
        "(nenhum par concorrente encontrado nesta execucao - "
        "gere mais eventos em paralelo e rode de novo)"
    )
