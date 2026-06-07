<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Nuevo Tour</h1>
        <p class="text-gray-500">Crea una nueva experiencia</p>
      </div>
      <NuxtLink to="/vendor/tours" class="text-gray-600 hover:text-gray-900">
        ← Volver
      </NuxtLink>
    </div>

    <TourForm />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth'],
})
</script>
