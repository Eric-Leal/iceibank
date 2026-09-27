class RelogioVetorial:
    def __init__(self, id_agencia, numero_agencias):
        self.id_agencia = id_agencia
        self.vetor = [0] * numero_agencias

    def evento_local(self):
        self.vetor[self.id_agencia] += 1
        return list(self.vetor)

    def ao_enviar(self):
        self.vetor[self.id_agencia] += 1
        return list(self.vetor)

    def ao_receber(self, vetor_recebido):
        for i in range(len(self.vetor)):
            self.vetor[i] = max(self.vetor[i], vetor_recebido[i])
        self.vetor[self.id_agencia] += 1
        return list(self.vetor)


if __name__ == "__main__":
    ag0 = RelogioVetorial(id_agencia=0, numero_agencias=3)
    ag1 = RelogioVetorial(id_agencia=1, numero_agencias=3)

    assert ag0.evento_local() == [1, 0, 0]
    assert ag1.evento_local() == [0, 1, 0]

    enviado = ag0.ao_enviar()
    assert enviado == [2, 0, 0]
    # destino fica com o maximo posicao a posicao e avanca a propria posicao
    assert ag1.ao_receber(enviado) == [2, 2, 0]

    # retorno e copia: alterar o que foi devolvido nao mexe no relogio
    copia = ag0.evento_local()
    copia[0] = 99
    assert ag0.vetor == [3, 0, 0]
    print("relogio vetorial OK")
