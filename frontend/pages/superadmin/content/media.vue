<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin'],
})

interface MediaFile {
  id: string
  filename: string
  original_name: string
  mime_type: string
  size_bytes: number
  size_formatted: string
  url: string
  thumbnail_url: string | null
  alt_text: string
  folder: string
  uploaded_by: string
  uploaded_at: string
  used_in: string[]
}

const api = useApi()
const toast = useToast()

const loading = ref(true)
const error = ref('')
const files = ref<MediaFile[]>([])
const currentFolder = ref('all')

const folders = computed(() => {
  const folderSet = new Set(files.value.map(f => f.folder))
  return ['all', ...Array.from(folderSet).sort()]
})

const filteredFiles = computed(() => {
  if (currentFolder.value === 'all') return files.value
  return files.value.filter(f => f.folder === currentFolder.value)
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

const deleteFile = async (file: MediaFile) => {
  try {
    await api.delete(`/superadmin/content/media/${file.id}`)
    files.value = files.value.filter(f => f.id !== file.id)
    toast.success('Archivo eliminado')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al eliminar archivo')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await api.get<MediaFile[]>('/superadmin/content/media')
    files.value = data
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar archivos'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-gray-500">Cargando...</p>
  </div>

  <div v-else-if="error" class="text-center py-12">
    <p class="text-red-500">{{ error }}</p>
  </div>

  <div v-else class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Media Library</h1>
        <p class="text-gray-500">{{ files.length }} archivos • {{ totalSize }} total</p>
      </div>
    </div>

    <!-- Folders -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="folder in folders"
        :key="folder"
        @click="currentFolder = folder"
        :class="[
          'px-4 py-2 rounded-lg text-sm font-medium capitalize',
          currentFolder === folder
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        {{ folder }}
      </button>
    </div>

    <!-- Media Grid -->
    <div v-if="filteredFiles.length === 0" class="text-center py-12 text-gray-400">
      No hay archivos en esta carpeta
    </div>
    <div v-else class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      <div
        v-for="file in filteredFiles"
        :key="file.id"
        class="bg-white rounded-lg shadow overflow-hidden group"
      >
        <div class="h-32 bg-gray-100 flex items-center justify-center">
          <img
            v-if="file.mime_type?.startsWith('image/')"
            :src="file.thumbnail_url || file.url"
            :alt="file.alt_text || file.filename"
            class="w-full h-full object-cover"
          />
          <span v-else class="text-4xl">📄</span>
        </div>
        <div class="p-3">
          <div class="text-sm font-medium text-gray-900 truncate" :title="file.filename">{{ file.filename }}</div>
          <div class="text-xs text-gray-500 flex justify-between mt-1">
            <span>{{ file.size_formatted }}</span>
            <span class="text-blue-600">{{ file.folder }}</span>
          </div>
        </div>
        <div class="px-3 pb-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button @click="deleteFile(file)" class="text-xs text-red-600 hover:text-red-800">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>
