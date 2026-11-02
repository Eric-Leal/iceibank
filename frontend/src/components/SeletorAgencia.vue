<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { AGENCIAS } from '@/types'

const auth = useAuthStore()
</script>

<template>
  <label class="block">
    <span class="mb-1 block text-sm font-medium">Agência de acesso</span>
    <select
      :value="auth.idAgencia"
      @change="auth.escolherAgencia(Number(($event.target as HTMLSelectElement).value))"
      class="campo"
    >
      <option v-for="agencia in AGENCIAS" :key="agencia.id" :value="agencia.id">
        Agência {{ agencia.id }} ({{ agencia.url }})
      </option>
    </select>
    <span class="mt-1 block text-xs text-slate-500">
      Cada agência só responde pelas contas com id % 3 igual ao seu número.
    </span>
  </label>
</template>
