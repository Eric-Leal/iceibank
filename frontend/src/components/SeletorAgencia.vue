<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { AGENCIAS } from '@/types'

const auth = useAuthStore()
</script>

<template>
  <label class="block">
    <span class="mb-1 block text-sm font-medium text-slate-700">Agencia de acesso</span>
    <select
      :value="auth.idAgencia"
      @change="auth.escolherAgencia(Number(($event.target as HTMLSelectElement).value))"
      class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none"
    >
      <option v-for="agencia in AGENCIAS" :key="agencia.id" :value="agencia.id">
        Agencia {{ agencia.id }} ({{ agencia.url }})
      </option>
    </select>
    <span class="mt-1 block text-xs text-slate-500">
      Cada agencia so responde pelas contas com id % 3 igual ao seu numero.
    </span>
  </label>
</template>
