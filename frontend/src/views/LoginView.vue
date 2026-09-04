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
  <div class="mx-auto max-w-md">
    <h2 class="mb-6 text-2xl font-semibold text-slate-800">Entrar</h2>

    <form @submit.prevent="entrar" class="space-y-4 rounded-xl border border-slate-200 bg-white p-6">
      <SeletorAgencia />

      <div class="flex gap-2">
        <button
          type="button"
          @click="perfil = 'cliente'"
          :class="[
            'flex-1 rounded-lg border px-3 py-2 text-sm font-medium',
            perfil === 'cliente'
              ? 'border-sky-600 bg-sky-600 text-white'
              : 'border-slate-300 text-slate-600',
          ]"
        >
          Cliente
        </button>
        <button
          type="button"
          @click="perfil = 'operador'"
          :class="[
            'flex-1 rounded-lg border px-3 py-2 text-sm font-medium',
            perfil === 'operador'
              ? 'border-sky-600 bg-sky-600 text-white'
              : 'border-slate-300 text-slate-600',
          ]"
        >
          Operador
        </button>
      </div>

      <label v-if="perfil === 'cliente'" class="block">
        <span class="mb-1 block text-sm font-medium text-slate-700">Numero da conta</span>
        <input
          v-model.number="idConta"
          type="number"
          required
          class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none"
        />
      </label>

      <label v-else class="block">
        <span class="mb-1 block text-sm font-medium text-slate-700">Usuario</span>
        <input
          v-model="usuario"
          required
          class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none"
        />
      </label>

      <label class="block">
        <span class="mb-1 block text-sm font-medium text-slate-700">Senha</span>
        <input
          v-model="senha"
          type="password"
          required
          class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none"
        />
      </label>

      <AlertaMensagem :erro="erro" />

      <button
        type="submit"
        :disabled="carregando"
        class="w-full rounded-lg bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700 disabled:opacity-50"
      >
        {{ carregando ? 'Entrando...' : 'Entrar' }}
      </button>
    </form>
  </div>
</template>
