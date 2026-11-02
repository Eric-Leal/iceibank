<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import AlertaMensagem from '@/components/AlertaMensagem.vue'
import Icone from '@/components/Icone.vue'
import PainelLideranca from '@/components/PainelLideranca.vue'
import { consultarSaldo, criarConta, depositar, sacar } from '@/services/api'
import { useAtividadesStore } from '@/stores/atividades'
import { useAuthStore } from '@/stores/auth'
import type { Conta } from '@/types'
import { formatarReais } from '@/utils/formatar'

const auth = useAuthStore()
const atividades = useAtividadesStore()

const idBusca = ref<number>(auth.idConta ?? 0)
const conta = ref<Conta | null>(null)
const saldoVisivel = ref(true)
const acao = ref<'depositar' | 'sacar' | null>(null)
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

async function operar() {
  if (!acao.value) return
  limparMensagens()
  try {
    const executar = acao.value === 'depositar' ? depositar : sacar
    conta.value = await executar(idBusca.value, valor.value)
    const nome = acao.value === 'depositar' ? 'Depósito' : 'Saque'
    sucesso.value = `${nome} de ${formatarReais(valor.value)} realizado.`
    atividades.registrar(
      nome,
      `Conta #${idBusca.value}`,
      acao.value === 'depositar' ? valor.value : -valor.value,
    )
    valor.value = 0
    acao.value = null
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
    atividades.registrar('Conta aberta', criada.nomeAluno, criada.saldo)
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
  <div class="space-y-8">
    <h1 class="text-2xl font-semibold">
      {{ conta ? `Olá, ${conta.nomeAluno.split(' ')[0]}` : 'Início' }}
    </h1>

    <AlertaMensagem :erro="erro" :sucesso="sucesso" />

    <div class="grid gap-6 lg:grid-cols-3">
      <section class="rounded-2xl border border-slate-200 bg-white lg:col-span-2">
        <div class="border-b border-slate-200 px-6 pt-4">
          <span class="inline-block border-b-2 border-marca-600 pb-3 text-sm font-semibold text-marca-700">
            Saldo
          </span>
        </div>

        <div class="p-6">
          <form v-if="auth.tipo === 'operador'" @submit.prevent="buscar" class="mb-5 flex gap-2">
            <input
              id="conta-busca"
              v-model.number="idBusca"
              type="number"
              aria-label="Número da conta"
              placeholder="Número da conta"
              class="w-48 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-marca-500 focus:outline-none"
            />
            <button class="rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900">
              Buscar
            </button>
          </form>

          <template v-if="conta">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div class="flex items-center gap-3">
                  <p class="text-4xl font-semibold tracking-tight">
                    {{ saldoVisivel ? formatarReais(conta.saldo) : 'R$ •••••' }}
                  </p>
                  <button
                    @click="saldoVisivel = !saldoVisivel"
                    :aria-label="saldoVisivel ? 'Ocultar saldo' : 'Mostrar saldo'"
                    class="text-marca-600 hover:text-marca-700"
                  >
                    <Icone :nome="saldoVisivel ? 'olho' : 'olhoFechado'" />
                  </button>
                </div>
                <p class="mt-1 text-sm text-slate-500">
                  Conta #{{ conta.id }} · Agência {{ auth.idAgencia }}
                </p>
              </div>

              <div class="flex gap-2">
                <button
                  @click="acao = acao === 'depositar' ? null : 'depositar'"
                  class="flex items-center gap-1.5 rounded-lg bg-marca-600 px-4 py-2 text-sm font-semibold text-white hover:bg-marca-700"
                >
                  <Icone nome="mais" :tamanho="16" /> Depositar
                </button>
                <button
                  @click="acao = acao === 'sacar' ? null : 'sacar'"
                  class="flex items-center gap-1.5 rounded-lg bg-marca-50 px-4 py-2 text-sm font-semibold text-marca-700 hover:bg-marca-100"
                >
                  <Icone nome="menos" :tamanho="16" /> Sacar
                </button>
                <RouterLink
                  to="/transferencia"
                  class="flex items-center gap-1.5 rounded-lg bg-marca-50 px-4 py-2 text-sm font-semibold text-marca-700 hover:bg-marca-100"
                >
                  <Icone nome="transferir" :tamanho="16" /> Transferir
                </RouterLink>
              </div>
            </div>

            <form
              v-if="acao"
              @submit.prevent="operar"
              class="mt-6 flex items-end gap-2 rounded-xl bg-slate-50 p-4"
            >
              <label class="flex-1">
                <span class="mb-1 block text-sm font-medium">
                  Valor do {{ acao === 'depositar' ? 'depósito' : 'saque' }}
                </span>
                <input
                  id="valor-operacao"
                  v-model.number="valor"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 focus:border-marca-500 focus:outline-none"
                />
              </label>
              <button class="rounded-lg bg-marca-600 px-5 py-2 font-semibold text-white hover:bg-marca-700">
                Confirmar
              </button>
            </form>
          </template>

          <p v-else class="text-sm text-slate-500">
            {{
              auth.tipo === 'operador'
                ? 'Busque uma conta para ver o saldo.'
                : erro
                  ? 'Saldo indisponível.'
                  : 'Carregando saldo...'
            }}
          </p>
        </div>
      </section>

      <PainelLideranca />
    </div>

    <section>
      <h2 class="mb-4 text-lg font-semibold">Últimas atividades</h2>
      <ul v-if="atividades.itens.length" class="divide-y divide-slate-200 rounded-2xl border border-slate-200 bg-white">
        <li v-for="(item, i) in atividades.itens" :key="i" class="flex items-center gap-4 px-6 py-4">
          <span class="w-12 text-sm text-slate-500">
            {{ item.quando.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }}
          </span>
          <span class="grid size-10 place-items-center rounded-full border border-slate-200 text-slate-600">
            <Icone :nome="item.valor >= 0 ? 'mais' : 'menos'" :tamanho="16" />
          </span>
          <div class="flex-1">
            <p class="text-sm font-semibold">{{ item.descricao }}</p>
            <p class="text-sm text-slate-500">{{ item.detalhe }}</p>
          </div>
          <span class="hidden items-center gap-1 text-sm font-medium text-marca-700 sm:flex">
            ✓ Aprovado
          </span>
          <span :class="['w-28 text-right text-sm font-semibold', item.valor >= 0 ? 'text-marca-700' : '']">
            {{ item.valor >= 0 ? '+' : '-' }} {{ formatarReais(Math.abs(item.valor)) }}
          </span>
        </li>
      </ul>
      <p v-else class="rounded-2xl border border-dashed border-slate-300 px-6 py-8 text-center text-sm text-slate-500">
        Nenhuma atividade nesta sessão ainda.
      </p>
    </section>

    <section v-if="auth.tipo === 'operador'" class="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 class="mb-4 text-lg font-semibold">Abrir conta</h2>

      <form @submit.prevent="abrirConta" class="grid gap-3 sm:grid-cols-2">
        <label class="block">
          <span class="mb-1 block text-sm font-medium">Número da conta</span>
          <input v-model.number="novaConta.id" type="number" required class="campo" />
        </label>
        <label class="block">
          <span class="mb-1 block text-sm font-medium">Nome do aluno</span>
          <input v-model="novaConta.nomeAluno" required class="campo" />
        </label>
        <label class="block">
          <span class="mb-1 block text-sm font-medium">Senha de acesso</span>
          <input v-model="novaConta.senha" type="password" required class="campo" />
        </label>
        <label class="block">
          <span class="mb-1 block text-sm font-medium">Saldo inicial (R$)</span>
          <input v-model.number="novaConta.saldoInicial" type="number" step="0.01" class="campo" />
        </label>
        <button
          type="submit"
          class="rounded-lg bg-marca-600 px-4 py-2.5 font-semibold text-white hover:bg-marca-700 sm:col-span-2"
        >
          Criar conta
        </button>
      </form>
    </section>
  </div>
</template>
