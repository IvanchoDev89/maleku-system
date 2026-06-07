<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

useSeo({
  title: 'Checkout',
  description: 'Completa tu reserva de viaje en Costa Rica de forma segura.'
})

const route = useRoute()

// Get params from URL
const totalPrice = ref(Number(route.query.total) || 2500)
const travelers = ref(Number(route.query.travelers) || 2)
const experienceName = ref(String(route.query.experience || 'Paquete Costa Rica'))

// Handle booking completion
const handleBookingComplete = (bookingData: any) => {
  // Redirect to success page with booking data
  navigateTo(`/checkout/success?booking=${bookingData.bookingId}`)
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
        Volver
      </button>

      <!-- Checkout Component -->
      <CheckoutWizard 
        :total-price="totalPrice"
        :travelers="travelers"
        :experience-name="experienceName"
        @complete="handleBookingComplete"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
