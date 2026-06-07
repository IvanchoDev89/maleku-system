<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

interface Props {
  currentPage: number
  totalPages: number
  totalItems: number
  itemsPerPage: number
}

const props = withDefaults(defineProps<Props>(), {
  currentPage: 1,
  totalPages: 1,
  totalItems: 0,
  itemsPerPage: 12
})

const emit = defineEmits<{
  (e: 'page-change', page: number): void
}>()

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = props.totalPages
  const current = props.currentPage

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }
  return pages
})

const fromItem = computed(() => Math.min((props.currentPage - 1) * props.itemsPerPage + 1, props.totalItems))
const toItem = computed(() => Math.min(props.currentPage * props.itemsPerPage, props.totalItems))

const goToPage = (page: number | string) => {
  if (typeof page === 'number' && page >= 1 && page <= props.totalPages) {
    emit('page-change', page)
  }
}
</script>

<template>
  <div class="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
    <div class="text-sm text-gray-600">
      Mostrando <span class="font-semibold text-gray-900">{{ fromItem }}</span>
      a <span class="font-semibold text-gray-900">{{ toItem }}</span>
      de <span class="font-semibold text-gray-900">{{ totalItems }}</span> resultados
    </div>

    <div class="flex items-center gap-1">
      <button
        :disabled="currentPage === 1"
        class="px-3 py-2 text-sm rounded-lg border transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        :class="currentPage === 1 ? 'text-gray-400 border-gray-200' : 'text-gray-700 border-gray-300'"
        @click="goToPage(currentPage - 1)"
      >
        <ChevronLeft class="w-5 h-5" />
      </button>

      <template v-for="(page, i) in visiblePages" :key="i">
        <button
          v-if="page !== '...'"
          class="w-10 h-10 text-sm rounded-lg border transition-colors"
          :class="page === currentPage
            ? 'bg-teal-600 text-white border-teal-600'
            : 'text-gray-700 border-gray-300 hover:bg-gray-50'"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
        <span v-else class="px-2 text-gray-400">...</span>
      </template>

      <button
        :disabled="currentPage === totalPages"
        class="px-3 py-2 text-sm rounded-lg border transition-colors disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        :class="currentPage === totalPages ? 'text-gray-400 border-gray-200' : 'text-gray-700 border-gray-300'"
        @click="goToPage(currentPage + 1)"
      >
        <ChevronRight class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>