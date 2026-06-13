<script setup lang="ts">
/**
 * Newsletter CTA Section
 * Captación de emails con incentivo - Conectado al backend
 */
import { ref } from 'vue'

const { subscribeNewsletter, pending } = useLandingData()

const email = ref('')
const firstName = ref('')
const isSubmitted = ref(false)
const submitMessage = ref('')
const isError = ref(false)

const handleSubmit = async () => {
  if (!email.value) return

  const result = await subscribeNewsletter(email.value, firstName.value || undefined)

  if (result.success) {
    isSubmitted.value = true
    isError.value = false
    submitMessage.value = result.message
  } else {
    isError.value = true
    submitMessage.value = result.message
  }
}
</script>

<template>
  <section class="py-20 bg-gradient-to-br from-primary-600 via-primary-800 to-secondary-500 relative overflow-hidden">
    <!-- Background Elements -->
    <div class="absolute inset-0">
      <div class="absolute top-0 left-0 w-96 h-96 bg-white/10 rounded-full -translate-x-1/2 -translate-y-1/2 blur-3xl"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 bg-white/10 rounded-full translate-x-1/2 translate-y-1/2 blur-3xl"></div>
    </div>

    <div class="container mx-auto px-4 relative z-10">
      <div class="max-w-3xl mx-auto text-center">
        <!-- Gift Icon -->
        <div class="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <span class="text-4xl">🎁</span>
        </div>

        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4">
          Obtén 10% de Descuento
        </h2>
        <p class="text-xl text-white/90 mb-2">
          En tu primera reserva
        </p>
        <p class="text-white/70 mb-8">
          Suscríbete y recibe ofertas exclusivas, guías de viaje y secretos locales de Costa Rica.
        </p>

        <!-- Form -->
        <Transition
          enter="transition-all duration-300"
          enter-from="opacity-0 translate-y-4"
          enter-to="opacity-100 translate-y-0"
          leave="transition-all duration-300"
          leave-from="opacity-100 translate-y-0"
          leave-to="opacity-0 -translate-y-4"
        >
          <form
            v-if="!isSubmitted"
            @submit.prevent="handleSubmit"
            class="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto"
          >
            <input
              v-model="email"
              type="email"
              placeholder="Tu correo electrónico"
              required
              class="flex-1 px-6 py-4 bg-white text-gray-900 rounded-full focus:ring-4 focus:ring-primary-300 focus:outline-none"
            />
            <button
              type="submit"
              :disabled="pending"
              class="px-8 py-4 bg-gray-900 hover:bg-gray-800 text-white font-bold rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {{ pending ? '...' : 'Suscribirme' }}
            </button>
          </form>

          <!-- Success/Error Message -->
          <div
            v-else
            :class="isError ? 'bg-red-500/20' : 'bg-white/20'"
            class="backdrop-blur-sm rounded-2xl p-8 max-w-lg mx-auto"
          >
            <div class="text-5xl mb-4">{{ isError ? '⚠️' : '✅' }}</div>
            <h3 class="text-2xl font-bold text-white mb-2">
              {{ isError ? 'Error' : '¡Bienvenido!' }}
            </h3>
            <p class="text-white/90">
              {{ submitMessage }}
            </p>
            <button
              v-if="isError"
              @click="isSubmitted = false; isError = false"
              class="mt-4 px-6 py-2 bg-white/20 hover:bg-white/30 text-white rounded-full transition-colors"
            >
              Intentar de nuevo
            </button>
          </div>
        </Transition>

        <!-- Trust Note -->
        <p class="mt-6 text-white/60 text-sm">
          🔒 No spam. Puedes darte de baja en cualquier momento.
        </p>
      </div>
    </div>
  </section>
</template>
