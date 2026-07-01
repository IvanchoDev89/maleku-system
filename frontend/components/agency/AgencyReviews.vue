<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900">Opiniones</h2>
      <div class="text-right">
        <StarRating :rating="averageRating" size="md" show-value />
        <p class="text-sm text-gray-500 mt-0.5">{{ total }} {{ total === 1 ? 'opinión' : 'opiniones' }}</p>
      </div>
    </div>

    <div v-if="reviews.length === 0" class="text-center py-8 text-gray-400">
      <Icon name="lucide:message-square" class="w-12 h-12 mx-auto mb-3 text-gray-300" />
      <p>No hay opiniones aún</p>
    </div>

    <div v-else class="space-y-5">
      <div v-for="review in reviews" :key="review.id" class="pb-5 border-b border-gray-100 last:border-0 last:pb-0">
        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold text-sm shrink-0">
            {{ review.user_name?.charAt(0)?.toUpperCase() || 'A' }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="font-medium text-gray-900 text-sm">{{ review.user_name || 'Anónimo' }}</span>
              <span class="text-gray-300">·</span>
              <span class="text-xs text-gray-400">{{ formatDate(review.created_at) }}</span>
            </div>
            <StarRating :rating="review.rating" size="sm" class="mb-2" />
            <p v-if="review.title" class="font-medium text-gray-800 text-sm">{{ review.title }}</p>
            <p v-if="review.comment" class="text-gray-600 text-sm mt-1 leading-relaxed">{{ review.comment }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AgencyLandingReview } from '~/types'

const props = defineProps<{
  reviews: AgencyLandingReview[]
  total: number
  averageRating: number
}>()

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>
