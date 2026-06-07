<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Editar Propiedad</h1>
        <p class="text-gray-500">Actualiza los detalles de tu alojamiento</p>
      </div>
      <NuxtLink to="/vendor/properties" class="text-gray-600 hover:text-gray-900 flex items-center gap-2">
        ← Volver a propiedades
      </NuxtLink>
    </div>
    <PropertyForm :property-id="propertyId" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const route = useRoute()
const propertyId = route.params.id as string
</script>
