<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function sair() {
  auth.sair()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-slate-100">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
        <div>
          <h1 class="text-lg font-semibold text-slate-800">ICEIBank</h1>
          <p class="text-xs text-slate-500">Agencia {{ auth.idAgencia }}</p>
        </div>

        <nav v-if="auth.autenticado" class="flex items-center gap-4 text-sm">
          <RouterLink to="/conta" class="text-slate-600 hover:text-sky-600">Conta</RouterLink>
          <RouterLink to="/transferencia" class="text-slate-600 hover:text-sky-600">
            Transferencia
          </RouterLink>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            {{ auth.tipo }}{{ auth.idConta !== null ? ` #${auth.idConta}` : '' }}
          </span>
          <button @click="sair" class="text-red-600 hover:text-red-700">Sair</button>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-4xl px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>
