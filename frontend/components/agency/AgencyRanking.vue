<template>
  <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200/60 p-6 sm:p-8 text-center">
    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-amber-100 text-amber-600 mb-4">
      <Icon name="lucide:trophy" class="w-8 h-8" />
    </div>
    <p class="text-3xl font-bold text-gray-900">#{{ ranking.position }}</p>
    <p class="text-gray-600 mt-1">de {{ ranking.total_vendors }} agencias</p>
    <div class="mt-3 flex items-center justify-center gap-2">
      <StarRating :rating="rating" size="sm" show-value />
      <span class="text-sm text-gray-500">promedio</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  ranking: {
    position: number
    total_vendors: number
  }
  rating: number
}>()
</script>
