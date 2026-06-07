<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <h1 class="text-3xl font-bold mb-8">Preguntas Frecuentes</h1>
      <div class="space-y-4">
        <div v-for="(item, i) in faqs" :key="i" class="bg-white p-6 rounded-lg shadow-sm">
          <h3 class="font-semibold text-lg mb-2">{{ item.q }}</h3>
          <p class="text-gray-600">{{ item.a }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
useSeo({
  title: 'Preguntas Frecuentes',
  description: 'Resuelve tus dudas sobre reservas, pagos y cancelaciones en Costa Rica Travel.'
})

const faqs = [
  { q: '¿Cómo puedo reservar?', a: 'Busca tours o hoteles y reserva directamente online.' },
  { q: '¿Política de cancelación?', a: 'Mayoría ofrece cancelación gratis hasta 48h antes.' },
  { q: '¿Métodos de pago?', a: 'Visa, Mastercard, Amex y PayPal.' },
  { q: '¿Puedo modificar mi reserva?', a: 'Sí, desde tu panel de cuenta.' }
]
</script>
