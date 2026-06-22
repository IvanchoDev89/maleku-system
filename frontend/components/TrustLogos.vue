<script setup lang="ts">
const partners = [
  { name: 'Booking.com', emoji: '🏨' },
  { name: 'TripAdvisor', emoji: '📋' },
  { name: 'Expedia', emoji: '✈️' },
  { name: 'Airbnb', emoji: '🏡' },
  { name: 'ICT Costa Rica', emoji: '🌴' },
  { name: 'Canatur', emoji: '🤝' }
]

const certifications = [
  { name: 'Certificación CST', badge: 'Sostenibilidad', icon: '♻️' },
  { name: 'Carbono Neutral', badge: '2030', icon: '🌱' },
  { name: 'Bandera Azul', badge: 'Playas', icon: '🏖️' }
]
</script>

<template>
  <section class="relative py-16 overflow-hidden bg-gray-50 dark:bg-gray-900/50 border-y border-gray-100 dark:border-gray-800">
    <div class="container mx-auto px-4">
      <div class="text-center mb-10">
        <p class="text-xs uppercase tracking-[0.2em] font-semibold text-gray-400 dark:text-gray-500">
          Confiado por viajeros de todo el mundo
        </p>
      </div>

      <div class="flex flex-wrap items-center justify-center gap-4 md:gap-8">
        <div
          v-for="partner in partners"
          :key="partner.name"
          class="group flex items-center gap-3 px-6 py-4 bg-white dark:bg-gray-800/80 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border border-gray-100 dark:border-gray-700/50"
        >
          <span class="text-2xl group-hover:scale-110 transition-transform duration-300">{{ partner.emoji }}</span>
          <span class="text-sm font-semibold text-gray-700 dark:text-gray-300 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{{ partner.name }}</span>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-center gap-3 mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
        <div
          v-for="cert in certifications"
          :key="cert.name"
          class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-full shadow-sm border border-gray-100 dark:border-gray-700"
        >
          <span class="text-lg">{{ cert.icon }}</span>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ cert.name }}</span>
          <span class="text-xs font-bold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-2 py-0.5 rounded-full">{{ cert.badge }}</span>
        </div>
      </div>
    </div>
  </section>
</template>
