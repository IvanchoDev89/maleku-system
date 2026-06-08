<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

useSeo({
  title: 'Checkout',
  description: 'Completa tu reserva de viaje en Costa Rica de forma segura.'
})

const route = useRoute()

// Query params (sent from /tours/[slug])
const totalPrice = ref(Number(route.query.total) || 0)
const travelers = ref(Number(route.query.travelers) || 2)
const experienceName = ref(String(route.query.experience || 'Paquete Costa Rica'))
const tourId = ref(String(route.query.tourId || ''))
const tourDate = ref(String(route.query.tourDate || ''))

// Handle booking completion
const handleBookingComplete = (bookingData: any) => {
  navigateTo(`/checkout/success?booking=${encodeURIComponent(bookingData.bookingId)}`)
}

const handleCancel = () => {
  navigateTo('/')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 py-8 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Back Link -->
      <button
        @click="handleCancel"
        class="mb-6 text-gray-600 hover:text-gray-900 flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        {{ $t('common.back') }}
      </button>

      <!-- Checkout Component -->
      <CheckoutWizard
        :total-price="totalPrice"
        :travelers="travelers"
        :experience-name="experienceName"
        :tour-id="tourId"
        :tour-date="tourDate"
        @complete="handleBookingComplete"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
