<script setup lang="ts">
import { computed, ref } from 'vue'

import AlertaMensagem from '@/components/AlertaMensagem.vue'
import { transferir } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { agenciaResponsavel } from '@/types'

const auth = useAuthStore()

const idOrigem = ref<number>(auth.idConta ?? 0)
const idDestino = ref<number>(0)
const valor = ref<number>(0)
const erro = ref('')
const sucesso = ref('')

// Nasce com a intencao de transferir, nao com o envio: dois cliques mandam o mesmo id.
const idOperacao = ref(crypto.randomUUID())

// A conta de destino pode estar em outra agencia. Quem resolve isso e o backend,
// mas mostramos o tipo previsto na tela para deixar a diferenca visivel.
const tipoTransferencia = computed(() =>
  agenciaResponsavel(idOrigem.value) === agenciaResponsavel(idDestino.value)
    ? 'local (mesma agencia)'
    : `entre agencias (${agenciaResponsavel(idOrigem.value)} -> ${agenciaResponsavel(idDestino.value)})`,
)

async function enviar() {
  erro.value = ''
  sucesso.value = ''
  try {
    const resposta = await transferir(
      idOrigem.value,
      idDestino.value,
      valor.value,
      idOperacao.value,
    )
    sucesso.value = resposta.mensagem
    valor.value = 0
    idOperacao.value = crypto.randomUUID()
  } catch (e) {
    erro.value = (e as Error).message
  }
}
</script>

<template>
  <div class="mx-auto max-w-xl">
    <h2 class="mb-4 text-xl font-semibold text-slate-800">Transferencia</h2>

    <form @submit.prevent="enviar" class="space-y-4 rounded-xl border border-slate-200 bg-white p-6">
      <label class="block">
        <span class="mb-1 block text-sm font-medium text-slate-700">Conta de origem</span>
        <input
          v-model.number="idOrigem"
          type="number"
          :disabled="auth.tipo === 'cliente'"
          required
          class="w-full rounded-lg border border-slate-300 px-3 py-2 disabled:bg-slate-100"
        />
      </label>

      <label class="block">
        <span class="mb-1 block text-sm font-medium text-slate-700">Conta de destino</span>
        <input
          v-model.number="idDestino"
          type="number"
          required
          class="w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </label>

      <label class="block">
        <span class="mb-1 block text-sm font-medium text-slate-700">Valor</span>
        <input
          v-model.number="valor"
          type="number"
          step="0.01"
          required
          class="w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </label>

      <p class="rounded-lg bg-slate-50 px-4 py-2 text-sm text-slate-600">
        Tipo previsto: <strong>{{ tipoTransferencia }}</strong>
      </p>

      <AlertaMensagem :erro="erro" :sucesso="sucesso" />

      <button
        type="submit"
        class="w-full rounded-lg bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700"
      >
        Transferir
      </button>
    </form>
  </div>
</template>
