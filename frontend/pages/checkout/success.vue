<script setup lang="ts">
import { Check, Download, Share2, MapPin, Calendar, Users, Mail } from 'lucide-vue-next'

const route = useRoute()
const bookingId = ref(String(route.query.booking || 'CR-2024-8847'))

const shareBooking = () => {
  if (navigator.share) {
    navigator.share({
      title: 'Mi viaje a Costa Rica confirmado',
      text: `¡Mi reserva ${bookingId.value} está confirmada!`,
      url: window.location.href
    })
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 py-12 px-4">
    <div class="max-w-2xl mx-auto">
      <!-- Success Card -->
      <div class="bg-white rounded-3xl shadow-xl p-8 text-center">
        <!-- Success Icon -->
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
              <p class="font-mono font-bold text-primary-600 text-lg">{{ bookingId }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Estado</p>
              <span class="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                <Check class="w-4 h-4" />
                Confirmado
              </span>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Fecha de llegada</p>
              <p class="font-medium text-gray-900">15 de marzo, 2024</p>
            </div>
            <div>
              <p class="text-sm text-gray-500 mb-1">Viajeros</p>
              <p class="font-medium text-gray-900">2 personas</p>
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
            to="/dashboard/traveler"
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
