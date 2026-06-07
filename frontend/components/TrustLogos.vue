<script setup lang="ts">
/**
 * Trust Logos Section
 * Logo cloud de partners y certificaciones
 */
const partners = [
  { name: 'Booking.com', logo: '/images/partners/booking.svg' },
  { name: 'TripAdvisor', logo: '/images/partners/tripadvisor.svg' },
  { name: 'Expedia', logo: '/images/partners/expedia.svg' },
  { name: 'Airbnb', logo: '/images/partners/airbnb.svg' },
  { name: 'ICT Costa Rica', logo: '/images/partners/ict.svg' },
  { name: 'Canatur', logo: '/images/partners/canatur.svg' }
]

const certifications = [
  { name: 'Certificación CST', badge: 'Level 5' },
  { name: 'Carbon Neutral', badge: '2024' },
  { name: 'Blue Flag', badge: 'Beaches' }
]
</script>

<template>
  <section class="py-12 bg-white border-b border-gray-100">
    <div class="container mx-auto px-4">
      <!-- Partners Logos -->
      <div class="text-center mb-8">
        <p class="text-sm text-gray-600 uppercase tracking-wider font-medium">
          Confiado por viajeros y respaldado por los mejores
        </p>
      </div>
      
      <!-- Logos Grid -->
      <div class="flex flex-wrap items-center justify-center gap-8 md:gap-12 opacity-60">
        <!-- Using text placeholders until real logos available -->
        <div class="flex items-center gap-8">
          <span class="text-xl font-bold text-blue-600">Booking.com</span>
          <span class="text-xl font-bold text-green-600">TripAdvisor</span>
          <span class="text-xl font-bold text-yellow-600">Expedia</span>
          <span class="text-xl font-bold text-red-500">Airbnb</span>
          <span class="text-xl font-bold text-blue-800">ICT Costa Rica</span>
          <span class="text-xl font-bold text-teal-600">Canatur</span>
        </div>
      </div>

      <!-- Certifications -->
      <div class="flex flex-wrap items-center justify-center gap-4 mt-8 pt-8 border-t border-gray-100">
        <div 
          v-for="cert in certifications" 
          :key="cert.name"
          class="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-full"
        >
          <span class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
          </span>
          <span class="text-sm font-medium text-gray-700">{{ cert.name }}</span>
          <span class="text-xs text-gray-700 bg-white px-2 py-0.5 rounded">{{ cert.badge }}</span>
        </div>
      </div>
    </div>
  </section>
</template>
