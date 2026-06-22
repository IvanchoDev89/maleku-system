<script setup lang="ts">
useSeo({
  title: 'Checkout',
  description: 'Completa tu reserva de viaje en Costa Rica de forma segura.'
})

const route = useRoute()

// Property booking params
const roomId = computed(() => String(route.query.roomId || ''))
const propertyId = computed(() => String(route.query.propertyId || ''))
const checkIn = computed(() => String(route.query.checkIn || ''))
const checkOut = computed(() => String(route.query.checkOut || ''))
const roomName = computed(() => String(route.query.roomName || ''))
const pax = computed(() => Number(route.query.guests || 2))

// Tour booking params
const totalPrice = computed(() => Number(route.query.total) || 0)
const travelers = computed(() => Number(route.query.travelers) || 2)
const experienceName = computed(() => String(route.query.experience || 'Paquete Costa Rica'))
const tourId = computed(() => String(route.query.tourId || ''))
const tourDate = computed(() => String(route.query.tourDate || ''))

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
      <button
        @click="handleCancel"
        class="mb-6 text-gray-600 hover:text-gray-900 flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        {{ $t('common.back') }}
      </button>

      <CheckoutWizard
        :total-price="totalPrice"
        :travelers="travelers"
        :experience-name="experienceName"
        :tour-id="tourId"
        :tour-date="tourDate"
        :room-id="roomId"
        :property-id="propertyId"
        :check-in="checkIn"
        :check-out="checkOut"
        :room-name="roomName"
        :guests="pax"
        @complete="handleBookingComplete"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
