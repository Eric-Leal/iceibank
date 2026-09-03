<script setup lang="ts">
import { onMounted, ref } from 'vue'

import AlertaMensagem from '@/components/AlertaMensagem.vue'
import { consultarSaldo, criarConta, depositar, sacar } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Conta } from '@/types'

const auth = useAuthStore()

const idBusca = ref<number>(auth.idConta ?? 0)
const conta = ref<Conta | null>(null)
const valor = ref<number>(0)
const erro = ref('')
const sucesso = ref('')

// Campos usados apenas pelo operador, para abrir uma conta nova
const novaConta = ref({ id: 0, nomeAluno: '', senha: '', saldoInicial: 0 })

function limparMensagens() {
  erro.value = ''
  sucesso.value = ''
}

async function buscar() {
  limparMensagens()
  try {
    conta.value = await consultarSaldo(idBusca.value)
  } catch (e) {
    conta.value = null
    erro.value = (e as Error).message
  }
}

async function operar(acao: 'depositar' | 'sacar') {
  limparMensagens()
  try {
    const executar = acao === 'depositar' ? depositar : sacar
    conta.value = await executar(idBusca.value, valor.value)
    sucesso.value = `${acao === 'depositar' ? 'Deposito' : 'Saque'} de R$ ${valor.value.toFixed(2)} realizado.`
    valor.value = 0
  } catch (e) {
    erro.value = (e as Error).message
  }
}

async function abrirConta() {
  limparMensagens()
  try {
    const criada = await criarConta(
      novaConta.value.id,
      novaConta.value.nomeAluno,
      novaConta.value.senha,
      novaConta.value.saldoInicial,
    )
    sucesso.value = `Conta ${criada.id} criada para ${criada.nomeAluno}.`
    novaConta.value = { id: 0, nomeAluno: '', senha: '', saldoInicial: 0 }
  } catch (e) {
    erro.value = (e as Error).message
  }
}

onMounted(() => {
  if (auth.tipo === 'cliente') buscar()
})
</script>

<template>
  <div class="mx-auto max-w-xl space-y-6">
    <section class="rounded-xl border border-slate-200 bg-white p-6">
      <h2 class="mb-4 text-xl font-semibold text-slate-800">Consultar saldo</h2>

      <div class="flex gap-2">
        <input
          v-model.number="idBusca"
          type="number"
          :disabled="auth.tipo === 'cliente'"
          class="flex-1 rounded-lg border border-slate-300 px-3 py-2 disabled:bg-slate-100"
        />
        <button
          @click="buscar"
          class="rounded-lg bg-slate-800 px-4 py-2 font-medium text-white hover:bg-slate-900"
        >
          Buscar
        </button>
      </div>

      <div v-if="conta" class="mt-4 rounded-lg bg-slate-50 p-4">
        <p class="text-sm text-slate-500">Conta {{ conta.id }} &middot; {{ conta.nomeAluno }}</p>
        <p class="text-3xl font-semibold text-slate-800">R$ {{ conta.saldo.toFixed(2) }}</p>
      </div>
    </section>

    <section v-if="conta" class="rounded-xl border border-slate-200 bg-white p-6">
      <h2 class="mb-4 text-xl font-semibold text-slate-800">Deposito e saque</h2>

      <div class="flex gap-2">
        <input
          v-model.number="valor"
          type="number"
          step="0.01"
          placeholder="Valor"
          class="flex-1 rounded-lg border border-slate-300 px-3 py-2"
        />
        <button
          @click="operar('depositar')"
          class="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
        >
          Depositar
        </button>
        <button
          @click="operar('sacar')"
          class="rounded-lg bg-amber-600 px-4 py-2 font-medium text-white hover:bg-amber-700"
        >
          Sacar
        </button>
      </div>
    </section>

    <section v-if="auth.tipo === 'operador'" class="rounded-xl border border-slate-200 bg-white p-6">
      <h2 class="mb-4 text-xl font-semibold text-slate-800">Abrir conta</h2>

      <form @submit.prevent="abrirConta" class="grid grid-cols-2 gap-3">
        <input
          v-model.number="novaConta.id"
          type="number"
          placeholder="Numero"
          required
          class="rounded-lg border border-slate-300 px-3 py-2"
        />
        <input
          v-model="novaConta.nomeAluno"
          placeholder="Nome"
          required
          class="rounded-lg border border-slate-300 px-3 py-2"
        />
        <input
          v-model="novaConta.senha"
          type="password"
          placeholder="Senha"
          required
          class="rounded-lg border border-slate-300 px-3 py-2"
        />
        <input
          v-model.number="novaConta.saldoInicial"
          type="number"
          step="0.01"
          placeholder="Saldo inicial"
          class="rounded-lg border border-slate-300 px-3 py-2"
        />
        <button
          type="submit"
          class="col-span-2 rounded-lg bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700"
        >
          Criar conta
        </button>
      </form>
    </section>

    <AlertaMensagem :erro="erro" :sucesso="sucesso" />
  </div>
</template>
