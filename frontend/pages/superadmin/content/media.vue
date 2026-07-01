<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin'],
})

const api = useApi()
const toast = useToast()

const loading = ref(true)
const uploading = ref(false)
const error = ref('')
const files = ref<MediaFile[]>([])
const currentFolder = ref('all')
const fileInput = ref<HTMLInputElement | null>(null)
const confirmDeleteId = ref<string | null>(null)

const folders = computed(() => {
  const folderSet = new Set(files.value.map(f => f.folder || 'general'))
  return ['all', ...Array.from(folderSet).sort()]
})

const filteredFiles = computed(() => {
  if (currentFolder.value === 'all') return files.value
  return files.value.filter(f => (f.folder || 'general') === currentFolder.value)
})

const totalSize = computed(() => {
  const bytes = files.value.reduce((sum, f) => sum + (f.size_bytes || 0), 0)
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return `${size.toFixed(1)} ${units[i]}`
})

const triggerUpload = () => fileInput.value?.click()

const handleFileSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  uploading.value = true
  try {
    await api.upload('/upload/image', file, 'file', currentFolder.value === 'all' ? 'general' : currentFolder.value)
    toast.success('Archivo subido exitosamente')
    loadFiles()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al subir archivo')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

const deleteFile = async (file: MediaFile) => {
  if (confirmDeleteId.value !== file.id) {
    confirmDeleteId.value = file.id
    setTimeout(() => { confirmDeleteId.value = null }, 3000)
    return
  }
  try {
    await api.delete(`/superadmin/content/media/${file.id}`)
    files.value = files.value.filter(f => f.id !== file.id)
    toast.success('Archivo eliminado')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al eliminar archivo')
  } finally {
    confirmDeleteId.value = null
  }
}

const loadFiles = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.get<MediaFile[]>('/superadmin/content/media')
    files.value = data
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar archivos'
  } finally {
    loading.value = false
  }
}

onMounted(loadFiles)
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Media Library</h1>
        <p class="text-gray-500 text-sm">{{ files.length }} archivos • {{ totalSize }} total</p>
      </div>
      <div>
        <input
          ref="fileInput"
          type="file"
          class="hidden"
          accept="image/*,.pdf,.doc,.docx"
          @change="handleFileSelected"
        />
        <button
          @click="triggerUpload"
          :disabled="uploading"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          <UiSpinner v-if="uploading" size="sm" color="white" />
          {{ uploading ? 'Subiendo...' : 'Subir Archivo' }}
        </button>
      </div>
    </div>

    <!-- Folders -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="folder in folders"
        :key="folder"
        @click="currentFolder = folder"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors',
          currentFolder === folder
            ? 'bg-primary-600 text-white shadow-sm'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
        ]"
      >
        {{ folder === 'all' ? 'Todas' : folder }}
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <UiSkeleton v-for="i in 12" :key="i" variant="image" />
    </div>

    <!-- Error state -->
    <UiAlert v-else-if="error" variant="error" dismissible @dismiss="error = ''">
      {{ error }}
    </UiAlert>

    <!-- Empty state -->
    <UiEmptyState
      v-else-if="filteredFiles.length === 0"
      title="No hay archivos"
      :description="currentFolder === 'all' ? 'Sube tu primer archivo para comenzar' : 'Esta carpeta está vacía'"
    >
      <button @click="triggerUpload" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium">
        Subir Archivo
      </button>
    </UiEmptyState>

    <!-- Media grid -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <div
        v-for="file in filteredFiles"
        :key="file.id"
        class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden group transition-shadow hover:shadow-md"
      >
        <div class="h-32 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
          <img
            v-if="file.mime_type?.startsWith('image/')"
            :src="file.thumbnail_url || file.url"
            :alt="file.alt_text || file.filename"
            class="w-full h-full object-cover"
          />
          <svg v-else class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="p-3">
          <div class="text-sm font-medium text-gray-900 dark:text-white truncate" :title="file.filename">{{ file.filename }}</div>
          <div class="text-xs text-gray-500 flex justify-between mt-1">
            <span>{{ file.size_formatted }}</span>
            <span class="text-primary-600">{{ file.folder }}</span>
          </div>
        </div>
        <div class="px-3 pb-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            @click="deleteFile(file)"
            :class="confirmDeleteId === file.id ? 'text-red-700 font-bold' : 'text-red-600 hover:text-red-800 dark:hover:text-red-400'"
            class="text-xs"
          >
            {{ confirmDeleteId === file.id ? '¿Confirmar?' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
