<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { BlogPost } from '~/types'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const posts = ref<BlogPost[]>([])
const loading = ref(true)

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
  { value: 'published', label: 'Published' },
  { value: 'draft', label: 'Draft' },
  { value: 'scheduled', label: 'Scheduled' },
]

const filterStatus = ref<string>('all')
const searchQuery = ref('')

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
  scheduled: 'bg-blue-100 text-blue-800',
  archived: 'bg-red-100 text-red-800'
}

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
    'Delete Post',
    'Are you sure you want to delete this post?',
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
      <h1 class="text-2xl font-bold text-gray-900">Blog Posts</h1>
      <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
        + New Post
      </button>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search posts..."
          class="flex-1 px-4 py-2 border rounded-lg"
        />
        <UiSelect v-model="filterStatus" :options="statusOptions" placeholder="All Status" />
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Author</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Views</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody v-if="loading" class="divide-y divide-gray-200">
          <tr>
            <td colspan="6" class="px-6 py-12 text-center text-gray-500">Cargando...</td>
          </tr>
        </tbody>
        <tbody v-else class="divide-y divide-gray-200">
          <tr v-for="post in filteredPosts" :key="post.id">
            <td class="px-6 py-4">
              <div class="font-medium text-gray-900">{{ post.title }}</div>
              <div class="text-sm text-gray-500">/{{ post.slug }}</div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ post.author }}</td>
            <td class="px-6 py-4">
              <span :class="['px-2 py-1 text-xs rounded-full', statusColors[post.status]]">
                {{ post.status }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ post.views }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ post.published_at || post.created_at }}
            </td>
            <td class="px-6 py-4 text-right space-x-2">
              <button class="text-blue-600 hover:text-blue-900 text-sm">Edit</button>
              <button @click="confirmDeletePost(post.id)" class="text-red-600 hover:text-red-900 text-sm">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
