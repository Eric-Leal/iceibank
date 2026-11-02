<script setup lang="ts">
import { computed, ref } from 'vue'

import AlertaMensagem from '@/components/AlertaMensagem.vue'
import { transferir } from '@/services/api'
import { useAtividadesStore } from '@/stores/atividades'
import { useAuthStore } from '@/stores/auth'
import { agenciaResponsavel } from '@/types'

const auth = useAuthStore()
const atividades = useAtividadesStore()

const idOrigem = ref<number>(auth.idConta ?? 0)
const idDestino = ref<number>(0)
const valor = ref<number>(0)
const erro = ref('')
const sucesso = ref('')

// Nasce com a intencao de transferir, nao com o envio: dois cliques mandam o mesmo id.
const idOperacao = ref(crypto.randomUUID())

// A conta de destino pode estar em outra agencia. Quem resolve isso e o backend,
// mas mostramos o tipo previsto na tela para deixar a diferenca visivel.
const entreAgencias = computed(
  () => agenciaResponsavel(idOrigem.value) !== agenciaResponsavel(idDestino.value),
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
    atividades.registrar('Transferência enviada', `Para a conta #${idDestino.value}`, -valor.value)
    valor.value = 0
    idOperacao.value = crypto.randomUUID()
  } catch (e) {
    erro.value = (e as Error).message
  }
}
</script>

<template>
  <div class="mx-auto max-w-xl space-y-6">
    <h1 class="text-2xl font-semibold">Transferir</h1>

    <form @submit.prevent="enviar" class="space-y-5 rounded-2xl border border-slate-200 bg-white p-6">
      <div class="grid gap-4 sm:grid-cols-2">
        <label class="block">
          <span class="mb-1 block text-sm font-medium">Conta de origem</span>
          <input
            v-model.number="idOrigem"
            type="number"
            :disabled="auth.tipo === 'cliente'"
            required
            class="campo"
          />
        </label>

        <label class="block">
          <span class="mb-1 block text-sm font-medium">Conta de destino</span>
          <input v-model.number="idDestino" type="number" required class="campo" />
        </label>
      </div>

      <label class="block">
        <span class="mb-1 block text-sm font-medium">Valor</span>
        <div class="relative">
          <span class="absolute top-1/2 left-3 -translate-y-1/2 text-slate-400">R$</span>
          <input
            v-model.number="valor"
            type="number"
            step="0.01"
            min="0.01"
            required
            class="campo !py-3 !pl-10 text-xl font-semibold"
          />
        </div>
      </label>

      <div class="flex items-center justify-between rounded-xl bg-marca-50 px-4 py-3 text-sm">
        <span class="text-slate-600">Tipo previsto</span>
        <span class="font-semibold text-marca-700">
          {{
            entreAgencias
              ? `Entre agências (${agenciaResponsavel(idOrigem)} → ${agenciaResponsavel(idDestino)})`
              : 'Local (mesma agência)'
          }}
        </span>
      </div>

      <AlertaMensagem :erro="erro" :sucesso="sucesso" />

      <button
        type="submit"
        class="w-full rounded-lg bg-marca-600 px-4 py-3 font-semibold text-white hover:bg-marca-700"
      >
        Transferir
      </button>
    </form>
  </div>
</template>
