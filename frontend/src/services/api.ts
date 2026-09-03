import axios from 'axios'

import router from '@/router'
import { useAuthStore } from '@/stores/auth'
import { urlAgencia, type Conta, type RespostaLogin, type RespostaTransferencia } from '@/types'

const api = axios.create()

/**
 * Antes de cada requisicao: define a agencia como destino e injeta o token.
 * E o que evita repetir o cabecalho Authorization em cada chamada.
 */
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  config.baseURL = urlAgencia(auth.idAgencia)
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

/**
 * Depois de cada resposta: traduz o erro da API para uma mensagem legivel.
 * Um 401 significa token ausente, invalido ou expirado, entao a sessao cai
 * e o usuario volta para o login.
 */
api.interceptors.response.use(
  (resposta) => resposta,
  (erro) => {
    const detalhe = erro.response?.data?.detail

    if (erro.response?.status === 401) {
      useAuthStore().sair()
      router.push('/login')
      return Promise.reject(new Error(detalhe ?? 'Sessao expirada. Faca login novamente.'))
    }

    if (detalhe) return Promise.reject(new Error(detalhe))
    if (erro.request) return Promise.reject(new Error('Agencia fora do ar ou inacessivel.'))
    return Promise.reject(erro)
  },
)

export async function loginCliente(id: number, senha: string) {
  const { data } = await api.post<RespostaLogin>('/auth/login', { id, senha })
  return data
}

export async function loginOperador(usuario: string, senha: string) {
  const { data } = await api.post<RespostaLogin>('/auth/login-operador', { usuario, senha })
  return data
}

export async function criarConta(
  id: number,
  nomeAluno: string,
  senha: string,
  saldoInicial: number,
) {
  const { data } = await api.post<Conta>('/contas', { id, nomeAluno, senha, saldoInicial })
  return data
}

export async function consultarSaldo(id: number) {
  const { data } = await api.get<Conta>(`/contas/${id}`)
  return data
}

export async function depositar(id: number, valor: number) {
  const { data } = await api.post<Conta>(`/contas/${id}/depositar`, { valor })
  return data
}

export async function sacar(id: number, valor: number) {
  const { data } = await api.post<Conta>(`/contas/${id}/sacar`, { valor })
  return data
}

export async function transferir(idOrigem: number, idDestino: number, valor: number) {
  const { data } = await api.post<RespostaTransferencia>('/transferencias', {
    idOrigem,
    idDestino,
    valor,
  })
  return data
}
