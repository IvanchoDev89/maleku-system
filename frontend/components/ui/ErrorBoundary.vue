<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'

const error = ref<Error | null>(null)

onErrorCaptured((err) => {
  error.value = err
  return false
})

function retry() {
  error.value = null
}
</script>

<template>
  <div v-if="error" class="flex flex-col items-center justify-center py-12 px-4">
    <svg class="w-12 h-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <p class="text-gray-600 text-center mb-4">Algo salió mal al cargar esta sección.</p>
    <UiButton variant="outline" size="sm" @click="retry">
      Reintentar
    </UiButton>
  </div>
  <slot v-else />
</template>
