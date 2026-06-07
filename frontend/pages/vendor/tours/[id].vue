<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Editar Tour</h1>
        <p class="text-gray-500">Edita los detalles del tour</p>
      </div>
      <NuxtLink to="/vendor/tours" class="text-gray-600 hover:text-gray-900">
        ← Volver
      </NuxtLink>
    </div>

    <TourForm :tour-id="route.params.id as string" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth'],
})

const route = useRoute()
</script>
