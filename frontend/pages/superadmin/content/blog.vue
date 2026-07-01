<script setup lang="ts">
import type { BlogPost } from '~/types'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const posts = ref<BlogPost[]>([])
const loading = ref(true)
const filterStatus = ref<string>('all')
const searchQuery = ref('')

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null
let pendingDeleteId: string | null = null

function openConfirm(title: string, message: string, action: () => Promise<void>, options?: { confirmText?: string, variant?: 'danger' | 'warning' | 'info' }) {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmConfirmText.value = options?.confirmText || 'Confirmar'
  confirmVariant.value = options?.variant || 'danger'
  confirmAction = action
  showConfirm.value = true
}

async function executeConfirmAction() {
  if (!confirmAction) return
  confirmLoading.value = true
  try {
    await confirmAction()
  } finally {
    confirmLoading.value = false
    showConfirm.value = false
    confirmAction = null
  }
}

const statusOptions = [
  { value: 'all', label: 'Todos los estados' },
  { value: 'published', label: 'Published' },
  { value: 'draft', label: 'Draft' },
  { value: 'archived', label: 'Archived' },
]

const filteredPosts = computed(() => {
  return posts.value.filter(p => {
    const matchesStatus = filterStatus.value === 'all' || p.status === filterStatus.value
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesSearch
  })
})

const statusColors: Record<string, string> = {
  published: 'bg-green-100 text-green-800',
  draft: 'bg-gray-100 text-gray-800',
  archived: 'bg-red-100 text-red-800',
}

const columns = [
  { key: 'title', label: 'Título', sortable: true },
  { key: 'status', label: 'Estado', align: 'center' as const, width: '100px' },
  { key: 'views', label: 'Vistas', align: 'center' as const, width: '80px', hiddenOnMobile: true },
  { key: 'date', label: 'Fecha', hiddenOnMobile: true },
  { key: 'actions', label: 'Acciones', align: 'right' as const },
]

const loadPosts = async () => {
  loading.value = true
  try {
    const data = await api.get('/blog?page_size=100')
    posts.value = Array.isArray(data) ? data : data.items || data.results || []
  } catch (error) {
    console.error('Error loading posts:', error)
    toast.error('Error al cargar artículos')
  } finally {
    loading.value = false
  }
}

const confirmDeletePost = (id: string) => {
  pendingDeleteId = id
  openConfirm(
    'Eliminar Artículo',
    '¿Estás seguro de eliminar este artículo?',
    executeDeletePost
  )
}

const executeDeletePost = async () => {
  if (!pendingDeleteId) return
  try {
    await api.delete(`/blog/${pendingDeleteId}`)
    posts.value = posts.value.filter(p => p.id !== pendingDeleteId)
    toast.success('Artículo eliminado')
  } catch (error: any) {
    toast.error(error?.data?.detail || 'Error al eliminar')
  } finally {
    pendingDeleteId = null
  }
}

onMounted(loadPosts)
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Blog Posts</h1>
      <NuxtLink
        to="/superadmin/content/pages/new"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium inline-flex items-center gap-2"
      >
        + New Post
      </NuxtLink>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div class="flex gap-4">
        <UiInput
          :model-value="searchQuery"
          placeholder="Buscar artículos..."
          class="flex-1"
          @update:model-value="searchQuery = $event"
        />
        <UiSelect v-model="filterStatus" :options="statusOptions" />
      </div>
    </div>

    <UiTable
      :columns="columns"
      :rows="filteredPosts"
      :loading="loading"
      empty-title="No hay artículos"
      empty-description="Crea tu primer artículo para empezar"
    >
      <template #cell-title="{ row }">
        <NuxtLink :to="`/blog/${row.slug}`" class="font-medium text-gray-900 dark:text-white hover:text-primary-600">
          {{ row.title }}
        </NuxtLink>
        <div class="text-sm text-gray-500">{{ row.author }} • /{{ row.slug }}</div>
      </template>
      <template #cell-status="{ row }">
        <span :class="['px-2 py-1 text-xs rounded-full font-medium', statusColors[row.status] || 'bg-gray-100 text-gray-800']">
          {{ row.status }}
        </span>
      </template>
      <template #cell-views="{ row }">
        <span class="text-gray-600">{{ (row as any).views || 0 }}</span>
      </template>
      <template #cell-date="{ row }">
        <span class="text-gray-500">{{ row.published_at || row.created_at }}</span>
      </template>
      <template #cell-actions="{ row }">
        <div class="flex justify-end gap-2">
          <NuxtLink
            :to="`/blog/${row.slug}`"
            class="text-primary-600 hover:text-primary-900 dark:hover:text-primary-400 text-sm"
          >
            Editar
          </NuxtLink>
          <button
            @click.stop="confirmDeletePost(row.id)"
            class="text-red-600 hover:text-red-900 dark:hover:text-red-400 text-sm"
          >
            Eliminar
          </button>
        </div>
      </template>
    </UiTable>

    <UiConfirmDialog
      v-model="showConfirm"
      :title="confirmTitle"
      :message="confirmMessage"
      :confirm-text="confirmConfirmText"
      :variant="confirmVariant"
      :loading="confirmLoading"
      @confirm="executeConfirmAction"
    />
  </div>
</template>
