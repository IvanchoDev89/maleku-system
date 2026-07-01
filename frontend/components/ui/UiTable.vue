<script setup lang="ts">
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-vue-next'

interface Column {
  key: string
  label: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  hiddenOnMobile?: boolean
  hiddenOnTablet?: boolean
}

interface Props {
  columns: Column[]
  rows: any[]
  loading?: boolean
  selectable?: boolean
  stickyHeader?: boolean
  emptyTitle?: string
  emptyDescription?: string
  sortKey?: string
  sortDir?: 'asc' | 'desc'
  rowKey?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectable: false,
  stickyHeader: false,
  rowKey: 'id',
})

const emit = defineEmits<{
  'sort': [key: string, dir: 'asc' | 'desc']
  'select': [rows: any[]]
  'row-click': [row: any]
}>()

const selected = ref<Set<any>>(new Set())

watch(() => props.rows, () => selected.value.clear())

function toggleSelectAll() {
  if (selected.value.size === props.rows.length) {
    selected.value.clear()
  } else {
    selected.value = new Set(props.rows.map(r => r[props.rowKey]))
  }
  emit('select', props.rows.filter(r => selected.value.has(r[props.rowKey])))
}

function toggleRow(row: any) {
  const key = row[props.rowKey]
  if (selected.value.has(key)) {
    selected.value.delete(key)
  } else {
    selected.value.add(key)
  }
  emit('select', props.rows.filter(r => selected.value.has(r[props.rowKey])))
}

function handleSort(col: Column) {
  if (!col.sortable) return
  const newDir = props.sortKey === col.key && props.sortDir === 'asc' ? 'desc' : 'asc'
  emit('sort', col.key, newDir)
}

const sortIcon = (col: Column) => {
  if (!col.sortable) return null
  if (props.sortKey !== col.key) return ChevronsUpDown
  return props.sortDir === 'asc' ? ChevronUp : ChevronDown
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200" :class="{ '!border-collapse': stickyHeader }">
        <thead :class="[stickyHeader ? 'sticky top-0 z-10' : '', 'bg-gray-50']">
          <tr>
            <th v-if="selectable" class="px-4 py-3 text-left">
              <input
                type="checkbox"
                :checked="rows.length > 0 && selected.size === rows.length"
                :indeterminate="selected.size > 0 && selected.size < rows.length"
                class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                @change="toggleSelectAll"
              />
            </th>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="[
                'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider',
                col.align === 'center' ? 'text-center' : col.align === 'right' ? 'text-right' : 'text-left',
                col.sortable ? 'cursor-pointer hover:bg-gray-100 select-none' : '',
                col.hiddenOnMobile ? 'hidden sm:table-cell' : '',
                col.hiddenOnTablet ? 'hidden md:table-cell' : '',
              ]"
              :style="col.width ? { width: col.width } : undefined"
              @click="handleSort(col)"
            >
              <div class="flex items-center gap-1" :class="col.align === 'right' ? 'justify-end' : col.align === 'center' ? 'justify-center' : ''">
                {{ col.label }}
                <component :is="sortIcon(col)" v-if="col.sortable" class="w-3 h-3 text-gray-400" />
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading">
            <td :colspan="columns.length + (selectable ? 1 : 0)" class="p-8">
              <div class="space-y-3">
                <UiSkeleton v-for="i in 5" :key="i" variant="table-row" :lines="columns.length" />
              </div>
            </td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td :colspan="columns.length + (selectable ? 1 : 0)" class="p-8">
              <UiEmptyState
                :title="emptyTitle || 'Sin resultados'"
                :description="emptyDescription"
                compact
              />
            </td>
          </tr>
          <tr
            v-for="row in rows"
            :key="row[rowKey]"
            class="hover:bg-gray-50 transition-colors cursor-pointer"
            @click="$emit('row-click', row)"
          >
            <td v-if="selectable" class="px-4 py-4">
              <input
                type="checkbox"
                :checked="selected.has(row[rowKey])"
                class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                @change="toggleRow(row)"
              />
            </td>
            <td
              v-for="col in columns"
              :key="col.key"
              :class="[
                'px-6 py-4 whitespace-nowrap text-sm',
                col.align === 'center' ? 'text-center' : col.align === 'right' ? 'text-right' : 'text-left',
                col.hiddenOnMobile ? 'hidden sm:table-cell' : '',
                col.hiddenOnTablet ? 'hidden md:table-cell' : '',
              ]"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                <span class="text-gray-900">{{ row[col.key] }}</span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="$slots.footer" class="border-t border-gray-200 px-6 py-3 bg-gray-50">
      <slot name="footer" />
    </div>
  </div>
</template>
