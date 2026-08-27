class RelogioLamport:
    def __init__(self):
        self.contador = 0

    def evento_local(self):
        self.contador += 1
        return self.contador

    def ao_enviar(self):
        self.contador += 1
        return self.contador

    def ao_receber(self, timestamp_recebido):
        self.contador = max(self.contador, timestamp_recebido) + 1
        return self.contador


if __name__ == "__main__":
    r = RelogioLamport()
    assert r.evento_local() == 1
    assert r.ao_enviar() == 2
    # recebido menor que o local: contador local vence e ainda avanca
    assert r.ao_receber(1) == 3
    # recebido maior: adota o recebido e avanca
    assert r.ao_receber(10) == 11
    print("relogio de Lamport OK")
