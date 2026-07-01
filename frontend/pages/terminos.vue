<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const { data: page } = await useAsyncData('page-terminos', () =>
  $fetch<StaticPage>(`${apiBase}/pages/public/terminos`).catch(() => ({ title: '', content: '' }) as StaticPage)
)

useSeo({
  title: page.value?.meta_title || 'Términos y Condiciones',
  description: page.value?.meta_description || 'Términos y condiciones de uso de Costa Rica Travel para reservas y servicios.'
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-3xl font-bold mb-8">{{ page?.title || 'Términos y Condiciones' }}</h1>
      <div v-if="page?.content" class="prose max-w-none" v-html="page.content"></div>
      <div v-else class="prose max-w-none">
        <p class="mb-4">Bienvenido a Costa Rica Travel. Al usar nuestros servicios, aceptas estos términos.</p>
        <h2 class="text-xl font-semibold mt-6 mb-4">1. Servicios</h2>
        <p class="mb-4">Costa Rica Travel conecta viajeros con proveedores locales de hoteles, tours y experiencias.</p>
        <h2 class="text-xl font-semibold mt-6 mb-4">2. Reservas</h2>
        <p class="mb-4">Todas las reservas están sujetas a disponibilidad.</p>
        <h2 class="text-xl font-semibold mt-6 mb-4">3. Contacto</h2>
        <p>Para consultas: info@costaricatravel.dev</p>
      </div>
    </div>
  </div>
</template>
