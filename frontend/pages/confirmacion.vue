<script setup lang="ts">
import { Check, Download, Share2, MapPin, Calendar, Mail } from 'lucide-vue-next'
import type { Booking } from '~/types'

definePageMeta({
  middleware: []
})

const route = useRoute()
const api = useApi()

const bookingId = ref('')
const booking = ref<Booking | null>(null)
const loading = ref(false)
const error = ref(false)

const loadBooking = async (id: string) => {
  loading.value = true
  error.value = false
  try {
    booking.value = await api.get<Booking>(`/bookings/${id}`)
  } catch {
    error.value = true
    try { useToast().add('No se pudo cargar los detalles de la reserva', 'warning') } catch {}
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const id = String(route.query.booking || '')
  if (id) {
    bookingId.value = id
    loadBooking(id)
  } else {
    bookingId.value = ''
    error.value = true
  }
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric', month: 'long', day: 'numeric'
  })
}

const shareBooking = () => {
  if (navigator.share) {
    navigator.share({
      title: 'Mi viaje a Costa Rica confirmado',
      text: `¡Mi reserva ${booking.value?.confirmation_code || bookingId.value} está confirmada!`,
      url: window.location.href
    })
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 py-12 px-4">
    <div class="max-w-2xl mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-3xl shadow-xl p-8 text-center">
        <div class="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-6"></div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">Cargando reserva...</h2>
        <p class="text-gray-500">Estamos verificando los detalles de tu reserva</p>
      </div>

      <!-- Success Card -->
      <div v-else-if="booking" class="bg-white rounded-3xl shadow-xl p-8 text-center">
        <div class="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Check class="w-12 h-12 text-green-600" />
        </div>

        <h1 class="text-3xl font-bold text-gray-900 mb-4">
          ¡Reserva Confirmada!
        </h1>
        <p class="text-gray-600 mb-8">
          Tu aventura en Costa Rica está lista. Hemos enviado los detalles a tu email.
        </p>

        <!-- Booking Details -->
        <div class="bg-gray-50 rounded-2xl p-6 mb-8">
          <div class="grid md:grid-cols-2 gap-4 text-left">
            <div>
              <p class="text-sm text-gray-500 mb-1">Código de reserva</p>
              <p class="font-mono font-bold text-primary-600 text-lg">{{ booking.confirmation_code || booking.id.slice(0, 8) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Estado</p>
              <span class="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                <Check class="w-4 h-4" />
                {{ booking.status === 'confirmed' ? 'Confirmado' : booking.status === 'pending' ? 'Pendiente' : booking.status }}
              </span>
            </div>
            <div v-if="booking.check_in">
              <p class="text-sm text-gray-500 mb-1">Fecha de llegada</p>
              <p class="font-medium text-gray-900">{{ formatDate(booking.check_in) }}</p>
            </div>
            <div v-if="booking.guests">
              <p class="text-sm text-gray-500 mb-1">Viajeros</p>
              <p class="font-medium text-gray-900">{{ booking.guests }} {{ booking.guests === 1 ? 'persona' : 'personas' }}</p>
            </div>
          </div>
          <div v-if="booking.total_amount" class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex justify-between items-center">
              <p class="text-sm text-gray-500">Total pagado</p>
              <p class="text-2xl font-bold text-gray-900">${{ booking.total_amount.toLocaleString('es-CR') }}</p>
            </div>
          </div>
        </div>

        <!-- Next Steps -->
        <div class="text-left mb-8">
          <h3 class="font-bold text-gray-900 mb-4">¿Qué sigue?</h3>
          <ul class="space-y-3">
            <li class="flex items-start gap-3">
              <div class="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <Mail class="w-3 h-3 text-primary-600" />
              </div>
              <span class="text-gray-600">Revisa tu email para el itinerario completo</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <Download class="w-3 h-3 text-primary-600" />
              </div>
              <span class="text-gray-600">Descarga tu app para seguir el viaje en vivo</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <Calendar class="w-3 h-3 text-primary-600" />
              </div>
              <span class="text-gray-600">Agrega las fechas a tu calendario</span>
            </li>
          </ul>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink
            to="/"
            class="px-8 py-4 bg-primary-600 text-white rounded-xl font-bold hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
          >
            <MapPin class="w-5 h-5" />
            Ver mi viaje
          </NuxtLink>
          <button
            @click="shareBooking"
            class="px-8 py-4 bg-gray-100 text-gray-700 rounded-xl font-bold hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
          >
            <Share2 class="w-5 h-5" />
            Compartir
          </button>
        </div>
      </div>

      <!-- Error / No booking state -->
      <div v-else class="bg-white rounded-3xl shadow-xl p-8 text-center">
        <div class="w-24 h-24 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <MapPin class="w-12 h-12 text-amber-600" />
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ bookingId ? 'Reserva no encontrada' : 'Sin reserva' }}</h1>
        <p class="text-gray-600 mb-8">
          {{ bookingId ? 'No pudimos encontrar los detalles de tu reserva. Revisa tu email para la confirmación.' : 'No se proporcionó un código de reserva.' }}
        </p>
        <NuxtLink
          to="/"
          class="px-8 py-4 bg-primary-600 text-white rounded-xl font-bold hover:bg-primary-700 transition-colors inline-flex items-center gap-2"
        >
          <MapPin class="w-5 h-5" />
          Volver al inicio
        </NuxtLink>
      </div>

      <!-- Help Section -->
      <div class="mt-8 text-center">
        <p class="text-gray-500 text-sm">
          ¿Necesitas ayuda?
          <a href="mailto:soporte@costaricatravel.com" class="text-primary-600 hover:underline">
            Contacta a nuestro equipo
          </a>
        </p>
      </div>
    </div>
  </div>
</template>
