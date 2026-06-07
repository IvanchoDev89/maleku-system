<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Nueva Propiedad</h1>
        <p class="text-gray-500">Completa todos los detalles de tu alojamiento</p>
      </div>
      <NuxtLink to="/vendor/properties" class="text-gray-600 hover:text-gray-900 flex items-center gap-2">
        ← Volver a propiedades
      </NuxtLink>
    </div>
    <PropertyForm />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})
</script>
