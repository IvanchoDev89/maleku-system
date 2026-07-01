<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
    <h2 class="text-xl font-bold text-gray-900 mb-4">Deja tu opinión</h2>

    <div v-if="success" class="text-center py-6">
      <Icon name="lucide:check-circle" class="w-12 h-12 text-green-500 mx-auto mb-3" />
      <p class="text-green-600 font-medium">¡Gracias por tu opinión!</p>
      <p class="text-gray-500 text-sm mt-1">Tu reseña ha sido publicada.</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1.5">Calificación</label>
        <div class="flex items-center gap-1">
          <button
            v-for="i in 5"
            :key="i"
            type="button"
            @click="rating = i"
            class="text-2xl transition-colors hover:text-amber-400 focus:outline-none"
            :class="i <= rating ? 'text-amber-400' : 'text-gray-300'"
          >
            <Icon name="lucide:star" class="fill-current" />
          </button>
          <span v-if="rating" class="ml-2 text-sm text-gray-500">{{ ratingLabels[rating] }}</span>
        </div>
      </div>

      <div>
        <label for="review-title" class="block text-sm font-medium text-gray-700 mb-1.5">Título (opcional)</label>
        <input
          id="review-title"
          v-model="title"
          type="text"
          placeholder="Resume tu experiencia"
          class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-shadow"
          maxlength="100"
        />
      </div>

      <div>
        <label for="review-comment" class="block text-sm font-medium text-gray-700 mb-1.5">Comentario (opcional)</label>
        <textarea
          id="review-comment"
          v-model="comment"
          rows="4"
          placeholder="Comparte tu experiencia con otros viajeros..."
          class="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-shadow resize-none"
          maxlength="1000"
        />
        <p class="text-xs text-gray-400 mt-1 text-right">{{ comment.length }}/1000</p>
      </div>

      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

      <button
        type="submit"
        :disabled="rating === 0 || submitting"
        class="w-full py-2.5 px-4 rounded-xl text-sm font-semibold text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        :class="rating > 0 ? 'bg-primary-600 hover:bg-primary-700' : 'bg-gray-300'"
      >
        <Icon v-if="submitting" name="lucide:loader-2" class="w-4 h-4 animate-spin inline mr-2" />
        {{ submitting ? 'Enviando...' : 'Publicar opinión' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  bookingId: string
}>()

const emit = defineEmits<{
  submitted: []
}>()

const rating = ref(0)
const title = ref('')
const comment = ref('')
const submitting = ref(false)
const error = ref<string | null>(null)
const success = ref(false)

const ratingLabels: Record<number, string> = {
  1: 'Malo',
  2: 'Regular',
  3: 'Bueno',
  4: 'Muy bueno',
  5: 'Excelente',
}

const api = useApi()

const handleSubmit = async () => {
  if (rating.value === 0) return
  submitting.value = true
  error.value = null
  try {
    await api.post('/reviews', {
      booking_id: props.bookingId,
      rating: rating.value,
      title: title.value.trim() || null,
      comment: comment.value.trim() || null,
    })
    success.value = true
    emit('submitted')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al enviar la reseña'
  } finally {
    submitting.value = false
  }
}
</script>
