<script setup lang="ts">
defineProps<{
  erro?: string
  sucesso?: string
}>()
</script>

<template>
  <p v-if="erro" class="rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
    {{ erro }}
  </p>
  <p
    v-else-if="sucesso"
    class="rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
  >
    {{ sucesso }}
  </p>
</template>
