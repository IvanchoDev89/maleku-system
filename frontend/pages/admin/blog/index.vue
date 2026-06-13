<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex gap-4">
        <UiSelect v-model="statusFilter" :options="statusOptions" placeholder="Todos los estados" @update:model-value="statusFilter = $event" />
      </div>
      <NuxtLink to="/admin/blog/new" class="bg-primary hover:bg-primary-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-md hover:shadow-lg transition-all">
        + Nuevo Artículo
      </NuxtLink>
    </div>

    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 animate-pulse">
        <div class="h-48 bg-gray-200" />
        <div class="p-5 space-y-3">
          <div class="h-3 bg-gray-200 rounded w-20" />
          <div class="h-5 bg-gray-200 rounded w-3/4" />
          <div class="h-4 bg-gray-200 rounded w-full" />
          <div class="h-4 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="post in filteredPosts" :key="post.id" class="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-lg transition-all">
        <div class="h-48 bg-gradient-to-br from-primary/10 to-accent/10 relative">
          <NuxtImg v-if="post.featured_image" :src="post.featured_image" class="w-full h-full object-cover" width="400" height="200" format="webp" />
          <div v-else class="w-full h-full flex items-center justify-center text-6xl opacity-20">📝</div>
          <div class="absolute top-3 left-3">
            <UiBadge :variant="statusBadgeVariant(post.status)" size="sm">
              {{ getStatusLabel(post.status) }}
            </UiBadge>
          </div>
        </div>
        <div class="p-5">
          <div class="flex gap-2 mb-3">
            <span v-for="tag in post.tags?.slice(0, 2)" :key="tag" class="text-xs text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full">
              {{ tag }}
            </span>
          </div>
          <h3 class="text-gray-900 font-bold text-lg mb-2 line-clamp-2">{{ post.title }}</h3>
          <p class="text-gray-500 text-sm mb-4 line-clamp-2">{{ post.excerpt }}</p>
          <div class="flex justify-between items-center text-sm text-gray-400">
            <span>{{ formatDate(post.published_at || post.created_at) }}</span>
            <span class="flex items-center gap-1">{{ post.views_count || 0 }} 👁️</span>
          </div>
          <div class="flex gap-2 mt-4 pt-4 border-t border-gray-100">
            <NuxtLink :to="`/admin/blog/${post.id}`" class="flex-1 text-center bg-gray-100 hover:bg-gray-200 text-gray-700 py-2.5 rounded-xl text-sm font-medium transition-colors">
              ✏️ Editar
            </NuxtLink>
            <button @click="openDeleteDialog(post)" class="px-4 bg-gray-100 hover:bg-red-50 text-gray-400 hover:text-red-500 rounded-xl transition-colors">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="posts.length === 0 && !loading" class="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
      <p class="text-6xl mb-4">📝</p>
      <p class="text-gray-500 text-lg mb-2">No hay artículos aún</p>
      <NuxtLink to="/admin/blog/new" class="text-primary hover:underline font-medium">Crear primer artículo</NuxtLink>
    </div>

    <!-- Delete Confirmation -->
    <UiConfirmDialog
      :model-value="!!postToDelete"
      title="Eliminar Artículo"
      :message="`¿Estás seguro de eliminar &quot;${postToDelete?.title}&quot;? Esta acción no se puede deshacer.`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="postToDelete = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

const api = useApi()
const auth = useAuthStore()

interface BlogPost {
  id: string
  title: string
  slug: string
  excerpt: string | null
  content: string
  featured_image: string | null
  status: string
  tags: string[]
  views_count?: number
  published_at: string | null
  created_at: string
}

const posts = ref<BlogPost[]>([])
const statusFilter = ref('')
const loading = ref(false)
const postToDelete = ref<BlogPost | null>(null)
const deleting = ref(false)

const statusOptions = [
  { value: '', label: 'Todos los estados' },
  { value: 'published', label: 'Publicados' },
  { value: 'draft', label: 'Borradores' },
  { value: 'scheduled', label: 'Programados' },
  { value: 'archived', label: 'Archivados' }
]

const filteredPosts = computed(() => {
  if (!statusFilter.value) return posts.value
  return posts.value.filter(p => p.status === statusFilter.value)
})

function statusBadgeVariant(status: string) {
  const map: Record<string, string> = {
    published: 'success',
    draft: 'warning',
    scheduled: 'info',
    archived: 'default'
  }
  return (map[status] || 'default') as any
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    published: 'Publicado',
    draft: 'Borrador',
    scheduled: 'Programado',
    archived: 'Archivado'
  }
  return labels[status] || status
}

const formatDate = (date: string) => date ? new Date(date).toLocaleDateString('es-CR') : ''

const loadPosts = async () => {
  loading.value = true
  try {
    const data = await api.get('/blog?page_size=100')
    posts.value = data.items || []
  } catch (error) {
    console.error('Error loading posts:', error)
  } finally {
    loading.value = false
  }
}

const openDeleteDialog = (post: BlogPost) => {
  postToDelete.value = post
}

const confirmDelete = async () => {
  if (!postToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/blog/${postToDelete.value.id}`)
    postToDelete.value = null
    loadPosts()
  } catch (error) {
    console.error('Error deleting post:', error)
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  auth.initAuth()
  loadPosts()
})
</script>
