<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AlertaMensagem from '@/components/AlertaMensagem.vue'
import SeletorAgencia from '@/components/SeletorAgencia.vue'
import { loginCliente, loginOperador } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const perfil = ref<'cliente' | 'operador'>('cliente')
const idConta = ref<number>(0)
const usuario = ref('operador')
const senha = ref('')
// Quem chega aqui por um 401 traz o motivo na query, senao a mensagem se perderia na troca de tela.
const erro = ref(String(route.query.erro ?? ''))
const carregando = ref(false)

async function entrar() {
  erro.value = ''
  carregando.value = true
  try {
    if (perfil.value === 'cliente') {
      const resposta = await loginCliente(idConta.value, senha.value)
      auth.entrar(resposta.token, resposta.tipo, idConta.value)
    } else {
      const resposta = await loginOperador(usuario.value, senha.value)
      auth.entrar(resposta.token, resposta.tipo, null)
    }
    router.push('/conta')
  } catch (e) {
    erro.value = (e as Error).message
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="grid min-h-screen lg:grid-cols-2">
    <div class="hidden flex-col justify-between bg-marca-600 p-12 text-white lg:flex">
      <div class="flex items-center gap-2">
        <div class="grid size-10 place-items-center rounded-xl bg-white font-bold text-marca-600">IB</div>
        <span class="text-lg font-semibold">ICEIBank</span>
      </div>
      <p class="max-w-md text-lg text-marca-100">
        Saldo, depósito, saque e transferência entre as 3 agências.
      </p>
      <p class="text-sm text-marca-200">PUC Minas · Sprint 3</p>
    </div>

    <div class="flex items-center justify-center px-6 py-12">
      <form @submit.prevent="entrar" class="w-full max-w-sm space-y-5">
        <div>
          <h2 class="text-2xl font-semibold">Entrar</h2>
          <p class="mt-1 text-sm text-slate-500">Escolha a agência e informe seus dados.</p>
        </div>

        <div class="flex rounded-lg bg-slate-100 p-1">
          <button
            v-for="opcao in ['cliente', 'operador'] as const"
            :key="opcao"
            type="button"
            @click="perfil = opcao"
            :class="[
              'flex-1 rounded-md py-2 text-sm font-medium capitalize',
              perfil === opcao ? 'bg-white text-marca-700 shadow-sm' : 'text-slate-500',
            ]"
          >
            {{ opcao }}
          </button>
        </div>

        <SeletorAgencia />

        <label v-if="perfil === 'cliente'" class="block">
          <span class="mb-1 block text-sm font-medium">Número da conta</span>
          <input v-model.number="idConta" type="number" required class="campo" />
        </label>

        <label v-else class="block">
          <span class="mb-1 block text-sm font-medium">Usuário</span>
          <input v-model="usuario" required class="campo" />
        </label>

        <label class="block">
          <span class="mb-1 block text-sm font-medium">Senha</span>
          <input v-model="senha" type="password" required class="campo" />
        </label>

        <AlertaMensagem :erro="erro" />

        <button
          type="submit"
          :disabled="carregando"
          class="w-full rounded-lg bg-marca-600 px-4 py-2.5 font-semibold text-white hover:bg-marca-700 disabled:opacity-50"
        >
          {{ carregando ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>
