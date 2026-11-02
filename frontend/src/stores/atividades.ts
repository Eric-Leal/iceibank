import { ref } from 'vue'
import { defineStore } from 'pinia'

import type { Atividade } from '@/types'

// O backend nao tem extrato, entao a lista guarda so o que foi feito nesta sessao.
export const useAtividadesStore = defineStore('atividades', () => {
  const itens = ref<Atividade[]>([])

  function registrar(descricao: string, detalhe: string, valor: number) {
    itens.value.unshift({ descricao, detalhe, valor, quando: new Date() })
  }

  return { itens, registrar }
})
