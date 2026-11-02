<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'

import Icone from '@/components/Icone.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const menu = [
  { para: '/conta', rotulo: 'Início', icone: 'inicio' },
  { para: '/transferencia', rotulo: 'Transferir', icone: 'transferir' },
] as const

function sair() {
  auth.sair()
  router.push('/login')
}
</script>

<template>
  <RouterView v-if="!auth.autenticado" />

  <div v-else class="flex min-h-screen">
    <aside class="hidden w-60 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
      <div class="flex items-center gap-2 px-6 py-6">
        <div class="grid size-10 place-items-center rounded-xl bg-marca-500 font-bold text-white">
          IB
        </div>
        <span class="text-lg font-semibold">ICEIBank</span>
      </div>

      <nav class="flex-1 space-y-1 px-3">
        <RouterLink
          v-for="item in menu"
          :key="item.para"
          :to="item.para"
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
          active-class="bg-marca-50 font-semibold !text-marca-700"
        >
          <Icone :nome="item.icone" />
          {{ item.rotulo }}
        </RouterLink>
      </nav>

      <button
        @click="sair"
        class="m-3 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-500 hover:bg-red-50 hover:text-red-600"
      >
        <Icone nome="sair" />
        Sair
      </button>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col bg-slate-50">
      <header class="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <nav class="flex gap-4 text-sm md:hidden">
          <RouterLink v-for="item in menu" :key="item.para" :to="item.para" active-class="font-semibold text-marca-700">
            {{ item.rotulo }}
          </RouterLink>
          <button @click="sair" class="text-red-600">Sair</button>
        </nav>
        <span class="hidden text-sm text-slate-500 md:block">
          Conectado à Agência {{ auth.idAgencia }}
        </span>

        <div class="flex items-center gap-2 rounded-full border border-slate-200 py-1 pr-4 pl-1">
          <span class="grid size-8 place-items-center rounded-full bg-marca-100 text-marca-700">
            <Icone nome="usuario" :tamanho="16" />
          </span>
          <span class="text-sm font-medium">
            {{ auth.tipo === 'operador' ? 'Operador' : `Conta #${auth.idConta}` }}
          </span>
        </div>
      </header>

      <main class="mx-auto w-full max-w-6xl px-4 py-8 md:px-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>
