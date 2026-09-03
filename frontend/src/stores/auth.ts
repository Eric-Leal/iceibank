import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

/**
 * Guarda o token JWT e a agencia escolhida como porta de entrada.
 * Persiste no localStorage para sobreviver a um refresh da pagina.
 */
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const tipo = ref<string | null>(localStorage.getItem('tipo'))
  const idConta = ref<number | null>(Number(localStorage.getItem('idConta')) || null)
  const idAgencia = ref<number>(Number(localStorage.getItem('idAgencia')) || 0)

  const autenticado = computed(() => token.value !== null)

  function entrar(novoToken: string, novoTipo: string, conta: number | null) {
    token.value = novoToken
    tipo.value = novoTipo
    idConta.value = conta

    localStorage.setItem('token', novoToken)
    localStorage.setItem('tipo', novoTipo)
    if (conta !== null) localStorage.setItem('idConta', String(conta))
  }

  function sair() {
    token.value = null
    tipo.value = null
    idConta.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('tipo')
    localStorage.removeItem('idConta')
  }

  function escolherAgencia(id: number) {
    idAgencia.value = id
    localStorage.setItem('idAgencia', String(id))
  }

  return { token, tipo, idConta, idAgencia, autenticado, entrar, sair, escolherAgencia }
})
