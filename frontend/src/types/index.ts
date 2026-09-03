export interface Conta {
  id: number
  nomeAluno: string
  saldo: number
}

export interface RespostaLogin {
  token: string
  tipo: 'cliente' | 'operador'
  expiraEmMinutos: number
}

export interface RespostaTransferencia {
  mensagem: string
}

/** Porta da Agencia 0. As demais seguem em sequencia (8081, 8082, 8083). */
const PORTA_BASE = 8081
const NUMERO_AGENCIAS = 3

export const AGENCIAS = Array.from({ length: NUMERO_AGENCIAS }, (_, id) => ({
  id,
  url: `http://localhost:${PORTA_BASE + id}`,
}))

export function urlAgencia(idAgencia: number): string {
  return `http://localhost:${PORTA_BASE + idAgencia}`
}

/** Mesma regra de particionamento do backend: a conta pertence a agencia `id % 3`. */
export function agenciaResponsavel(idConta: number): number {
  return idConta % NUMERO_AGENCIAS
}
