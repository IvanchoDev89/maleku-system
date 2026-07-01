<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-3xl font-bold mb-8">{{ page?.title || 'Centro de Ayuda' }}</h1>
      <div v-if="page?.content" class="prose max-w-none" v-html="page.content"></div>
      <div v-else class="space-y-4">
        <div v-for="(item, i) in helpItems" :key="i" class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="font-semibold text-lg mb-2">{{ item.q }}</h3>
          <p class="text-gray-600">{{ item.a }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const { data: page } = await useAsyncData('page-ayuda', () =>
  $fetch<StaticPage>(`${apiBase}/pages/public/ayuda`).catch(() => null)
)

useSeo({
  title: page.value?.meta_title || 'Centro de Ayuda | Costa Rica Travel',
  description: page.value?.meta_description || 'Encuentra respuestas a preguntas frecuentes sobre reservas, pagos, cancelaciones y más.'
})

const fallbackHelp = [
  { q: '¿Cómo creo una cuenta?', a: 'Haz clic en "Registrarse" en la esquina superior derecha y completa el formulario con tus datos.' },
  { q: '¿Cómo puedo contactar a un proveedor?', a: 'Cada tour o propiedad tiene un botón de contacto directo. También puedes escribirnos a través del formulario en la página de contacto.' },
  { q: '¿Los precios incluyen impuestos?', a: 'Sí, todos los precios mostrados incluyen impuestos aplicables. Puedes ver el desglose completo antes de confirmar tu reserva.' },
  { q: '¿Cómo recibo mi confirmación de reserva?', a: 'Recibirás un correo electrónico con tu código de confirmación y los detalles de tu reserva inmediatamente después del pago.' },
  { q: '¿Puedo modificar una reserva existente?', a: 'Sí, puedes modificar o cancelar tu reserva desde tu panel de cuenta. Las políticas de cancelación varían según el proveedor.' },
]

const helpItems = page.value?.content ? [] : fallbackHelp
</script>
