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


if __name__ == "__main__":
    assert comparar_vetores([1, 2, 0], [1, 2, 0]) == "IGUAIS"
    assert comparar_vetores([1, 2, 0], [2, 2, 0]) == "ANTES"
    assert comparar_vetores([3, 2, 0], [2, 2, 0]) == "DEPOIS"
    assert comparar_vetores([3, 1, 0], [2, 2, 0]) == "CONCORRENTES"
    print("comparar_vetores OK")
