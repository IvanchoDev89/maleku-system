<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const pages = ref<StaticPage[]>([])
const loading = ref(true)
const confirmDeleteId = ref<string | null>(null)
const sortKey = ref<string>('sort_order')
const sortDir = ref<'asc' | 'desc'>('asc')

const columns = [
  { key: 'title', label: 'Página', sortable: true },
  { key: 'slug', label: 'Slug', sortable: true, hiddenOnMobile: true },
  { key: 'show_in_header', label: 'Header', align: 'center' as const, width: '80px' },
  { key: 'show_in_footer', label: 'Footer', align: 'center' as const, width: '80px' },
  { key: 'is_active', label: 'Activa', align: 'center' as const, width: '80px' },
  { key: 'actions', label: 'Acciones', align: 'right' as const },
]

const sortedPages = computed(() => {
  const sorted = [...pages.value]
  sorted.sort((a: any, b: any) => {
    const aVal = a[sortKey.value]
    const bVal = b[sortKey.value]
    if (typeof aVal === 'string') {
      return sortDir.value === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    }
    return sortDir.value === 'asc' ? (aVal - bVal) : (bVal - aVal)
  })
  return sorted
})

function handleSort(key: string, dir: 'asc' | 'desc') {
  sortKey.value = key
  sortDir.value = dir
}

const fetchPages = async () => {
  loading.value = true
  try {
    pages.value = await api.get<StaticPage[]>('/superadmin/content/pages')
  } catch (error: any) {
    toast.error(error?.data?.detail || 'Error al cargar páginas')
    pages.value = []
  } finally {
    loading.value = false
  }
}

const toggleActive = async (page: StaticPage) => {
  try {
    await api.put(`/superadmin/content/pages/${page.id}`, { is_active: !page.is_active })
    page.is_active = !page.is_active
    toast.success(`Página ${page.is_active ? 'activada' : 'desactivada'}`)
  } catch (error: any) {
    toast.error(error?.data?.detail || 'Error al cambiar estado')
  }
}

const deletePage = async (page: StaticPage) => {
  if (confirmDeleteId.value !== page.id) {
    confirmDeleteId.value = page.id
    setTimeout(() => { confirmDeleteId.value = null }, 3000)
    return
  }
  try {
    await api.delete(`/superadmin/content/pages/${page.id}`)
    pages.value = pages.value.filter(p => p.id !== page.id)
    toast.success('Página eliminada')
  } catch (error: any) {
    toast.error(error?.data?.detail || 'Error al eliminar página')
  } finally {
    confirmDeleteId.value = null
  }
}

onMounted(fetchPages)
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Páginas Estáticas</h1>
      <NuxtLink
        to="/superadmin/content/pages/new"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
      >
        + Nueva Página
      </NuxtLink>
    </div>

    <div v-if="loading" class="space-y-3">
      <UiSkeleton v-for="i in 5" :key="i" variant="table-row" :lines="6" />
    </div>

    <UiTable
      v-else
      :columns="columns"
      :rows="sortedPages"
      :loading="false"
      sort-key="sort_order"
      sort-dir="asc"
      empty-title="No hay páginas estáticas"
      empty-description="Crea tu primera página para empezar"
      @sort="handleSort"
    >
      <template #cell-title="{ row }">
        <NuxtLink :to="`/superadmin/content/pages/${row.id}`" class="font-medium text-gray-900 dark:text-white hover:text-primary-600">
          {{ row.title }}
        </NuxtLink>
        <div class="text-sm text-gray-500">{{ row.template || 'default' }}</div>
      </template>
      <template #cell-slug="{ row }">
        <span class="text-sm text-gray-500">/{{ row.slug }}</span>
      </template>
      <template #cell-show_in_header="{ row }">
        <span :class="row.show_in_header ? 'text-green-600' : 'text-gray-300'">{{ row.show_in_header ? '✓' : '—' }}</span>
      </template>
      <template #cell-show_in_footer="{ row }">
        <span :class="row.show_in_footer ? 'text-green-600' : 'text-gray-300'">{{ row.show_in_footer ? '✓' : '—' }}</span>
      </template>
      <template #cell-is_active="{ row }">
        <button @click="toggleActive(row)" :class="row.is_active ? 'text-green-600' : 'text-gray-300 hover:text-green-600'" class="transition-colors">
          {{ row.is_active ? '●' : '○' }}
        </button>
      </template>
      <template #cell-actions="{ row }">
        <div class="flex justify-end gap-2">
          <NuxtLink
            :to="`/superadmin/content/pages/${row.id}`"
            class="text-primary-600 hover:text-primary-900 dark:hover:text-primary-400 text-sm"
          >
            Editar
          </NuxtLink>
          <button
            @click="deletePage(row)"
            :class="confirmDeleteId === row.id ? 'text-red-700 font-bold' : 'text-red-600 hover:text-red-900 dark:hover:text-red-400'"
            class="text-sm"
          >
            {{ confirmDeleteId === row.id ? '¿Confirmar?' : 'Eliminar' }}
          </button>
        </div>
      </template>
    </UiTable>
  </div>
</template>
