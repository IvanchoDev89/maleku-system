<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const { data: page } = await useAsyncData('page-privacidad', () =>
  $fetch<StaticPage>(`${apiBase}/pages/public/privacidad`).catch(() => null)
)

useSeo({
  title: page.value?.meta_title || 'Política de Privacidad',
  description: page.value?.meta_description || 'Conoce cómo protegemos tu información personal en Costa Rica Travel.'
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-3xl font-bold mb-8">{{ page?.title || 'Política de Privacidad' }}</h1>
      <div v-if="page?.content" class="prose max-w-none" v-html="page.content"></div>
      <div v-else class="prose max-w-none">
        <p class="mb-4">En Costa Rica Travel, tu privacidad es importante para nosotros.</p>
        <h2 class="text-xl font-semibold mt-6 mb-4">1. Información que recopilamos</h2>
        <p class="mb-4">Recopilamos información necesaria para procesar reservas.</p>
        <h2 class="text-xl font-semibold mt-6 mb-4">2. Contacto</h2>
        <p>Para ejercer tus derechos: privacy@costaricatravel.dev</p>
      </div>
    </div>
  </div>
</template>
