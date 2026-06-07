<script setup lang="ts">
import { ref, computed } from 'vue'

interface Column {
  key: string
  label: string
  sortable?: boolean
  width?: string
}

interface Props {
  columns: Column[]
  rows: any[]
  loading?: boolean
  page?: number
  pageSize?: number
  total?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  page: 1,
  pageSize: 20,
  total: 0
})

const emit = defineEmits<{
  'sort': [key: string, direction: 'asc' | 'desc']
  'page': [value: number]
}>()

const sortKey = ref('')
const sortDir = ref<'asc' | 'desc'>('asc')

function toggleSort(key: string) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
  emit('sort', sortKey.value, sortDir.value)
}

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
</script>

<template>
  <div class="w-full overflow-x-auto rounded-xl border border-gray-200">
    <table class="w-full text-sm">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            :class="[
              'text-left py-3 px-4 font-semibold text-gray-600',
              col.sortable ? 'cursor-pointer select-none hover:text-gray-800' : '',
              col.width || ''
            ]"
            @click="col.sortable ? toggleSort(col.key) : undefined"
          >
            <div class="flex items-center gap-1">
              {{ col.label }}
              <svg v-if="col.sortable && sortKey === col.key" class="w-3.5 h-3.5 transition-transform" :class="sortDir === 'desc' ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
            </div>
          </th>
          <th v-if="$slots.actions" class="text-right py-3 px-4 font-semibold text-gray-600 w-24">Acciones</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-100">
        <tr v-if="loading" class="animate-pulse">
          <td v-for="col in columns" :key="col.key" class="py-4 px-4">
            <div class="h-4 bg-gray-200 rounded w-3/4" />
          </td>
          <td v-if="$slots.actions" class="py-4 px-4">
            <div class="h-4 bg-gray-200 rounded w-16 ml-auto" />
          </td>
        </tr>
        <tr v-else-if="!rows.length">
          <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="text-center py-12 text-gray-500">
            No hay datos disponibles.
          </td>
        </tr>
        <tr
          v-for="(row, idx) in rows"
          :key="row.id || idx"
          class="hover:bg-gray-50 transition-colors"
        >
          <td v-for="col in columns" :key="col.key" class="py-3 px-4">
            <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
          <td v-if="$slots.actions" class="py-3 px-4">
            <div class="flex justify-end gap-2">
              <slot name="actions" :row="row" />
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <Pagination
    v-if="total > pageSize"
    :current-page="page"
    :total-pages="totalPages"
    :total-items="total"
    :items-per-page="pageSize"
    @page-change="emit('page', $event)"
  />
</template>
