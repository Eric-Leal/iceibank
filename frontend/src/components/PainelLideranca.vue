<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import Icone from '@/components/Icone.vue'
import { consultarLider } from '@/services/api'
import { AGENCIAS } from '@/types'

const INTERVALO_MS = 3000

const lider = ref<number | null>(null)
const ativas = ref<Record<number, boolean>>({})
let temporizador: ReturnType<typeof setInterval> | undefined

async function atualizar() {
  const respostas = await Promise.allSettled(AGENCIAS.map((a) => consultarLider(a.id)))
  respostas.forEach((r, id) => (ativas.value[id] = r.status === 'fulfilled'))
  // Na transicao duas agencias podem discordar; vale a da agencia de maior id que respondeu.
  const conhecidas = respostas.flatMap((r) => (r.status === 'fulfilled' ? [r.value.liderAtual] : []))
  lider.value = conhecidas.filter((l) => l !== null).at(-1) ?? null
}

onMounted(() => {
  atualizar()
  temporizador = setInterval(atualizar, INTERVALO_MS)
})
onUnmounted(() => clearInterval(temporizador))
</script>

<template>
  <section class="flex flex-col rounded-2xl border border-slate-200 bg-white p-6">
    <div class="flex items-center justify-between">
      <h2 class="font-semibold">Líder atual</h2>
      <span class="flex items-center gap-1.5 text-xs text-slate-500">
        <span class="size-2 animate-pulse rounded-full bg-marca-500" />
        ao vivo
      </span>
    </div>

    <div class="mt-4 flex items-center gap-3">
      <span class="grid size-12 place-items-center rounded-xl bg-amber-100 text-amber-600">
        <Icone nome="coroa" :tamanho="24" />
      </span>
      <div>
        <p class="text-2xl font-semibold">
          {{ lider === null ? 'Sem líder' : `Agência ${lider}` }}
        </p>
        <p class="text-xs text-slate-500">Eleita pelo algoritmo de Bully</p>
      </div>
    </div>

    <ul class="mt-auto space-y-2 pt-5">
      <li
        v-for="agencia in AGENCIAS"
        :key="agencia.id"
        class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
      >
        <span>Agência {{ agencia.id }}</span>
        <span
          :class="[
            'flex items-center gap-1.5 text-xs font-medium',
            ativas[agencia.id] ? 'text-marca-700' : 'text-red-600',
          ]"
        >
          <span :class="['size-2 rounded-full', ativas[agencia.id] ? 'bg-marca-500' : 'bg-red-500']" />
          {{ ativas[agencia.id] ? 'Online' : 'Fora do ar' }}
        </span>
      </li>
    </ul>
  </section>
</template>
