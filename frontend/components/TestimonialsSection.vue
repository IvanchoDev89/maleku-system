<template>
  <section class="py-20 bg-gray-50">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-700 font-semibold rounded-full text-sm mb-4">
          {{ $t('testimonials.badge') }}
        </span>
        <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">{{ $t('testimonials.title') }}</h2>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        <div v-for="testimonial in testimonials" :key="testimonial.name" class="bg-white p-8 rounded-2xl shadow-sm">
          <div class="flex items-center gap-1 mb-4">
            <span v-for="n in 5" :key="n" class="text-yellow-400">★</span>
          </div>
          <p class="text-gray-700 mb-6 italic">"{{ testimonial.text }}"</p>
          <div class="flex items-center gap-4">
            <NuxtImg :src="testimonial.avatar" :alt="testimonial.name" class="w-12 h-12 rounded-full object-cover" width="48" height="48" format="webp" />
            <div>
              <div class="font-bold text-gray-900">{{ testimonial.name }}</div>
              <div class="text-sm text-gray-600">{{ testimonial.country }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { t } = useI18n()

const testimonials = [
  {
    name: 'Marie Dubois',
    country: 'Francia',
    text: 'Una experiencia increíble. Los eco-lodges eran perfectos y los tours muy bien organizados. ¡Volveré!',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&q=80'
  },
  {
    name: 'James Wilson',
    country: 'Estados Unidos',
    text: 'El planificador de viajes fue clave para optimizar nuestro tiempo. Todo funcionó a la perfección.',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80'
  },
  {
    name: 'Stefan Müller',
    country: 'Alemania',
    text: 'La mejor decisión fue contratar un guide local. Conocimos lugares que no aparecen en las guías.',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80'
  }
]
</script>