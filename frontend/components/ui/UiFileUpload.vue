<script setup lang="ts">
import { Upload, X, File, FileText, Image } from 'lucide-vue-next'

interface UploadedFile {
  id: string
  file: File
  preview?: string
  progress?: number
  error?: string
}

interface Props {
  modelValue?: UploadedFile[]
  label?: string
  description?: string
  accept?: string
  multiple?: boolean
  maxSize?: number
  maxFiles?: number
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  accept: 'image/*,.pdf,.doc,.docx',
  multiple: true,
  maxSize: 10 * 1024 * 1024,
  maxFiles: 10,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [files: UploadedFile[]]
  'files-added': [files: UploadedFile[]]
  'file-removed': [file: UploadedFile]
}>()

const files = ref<UploadedFile[]>([])
const isDragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const dropZoneRef = ref<HTMLDivElement | null>(null)

watch(() => props.modelValue, (val) => {
  if (val) files.value = val
}, { immediate: true })

function addFiles(newFiles: FileList | File[]) {
  const arr = Array.from(newFiles)
  const remaining = props.maxFiles - files.value.length
  if (remaining <= 0) return

  const toAdd = arr.slice(0, remaining)
  const added: UploadedFile[] = []

  for (const file of toAdd) {
    if (file.size > props.maxSize) {
      added.push({ id: crypto.randomUUID(), file, error: `Excede ${(props.maxSize / 1024 / 1024).toFixed(0)}MB` })
      continue
    }
    const entry: UploadedFile = { id: crypto.randomUUID(), file }
    if (file.type.startsWith('image/')) {
      entry.preview = URL.createObjectURL(file)
    }
    added.push(entry)
  }

  files.value = [...files.value, ...added]
  emit('update:modelValue', files.value)
  emit('files-added', added)
}

function removeFile(file: UploadedFile) {
  if (file.preview) URL.revokeObjectURL(file.preview)
  files.value = files.value.filter(f => f.id !== file.id)
  emit('update:modelValue', files.value)
  emit('file-removed', file)
}

function onDrop(event: DragEvent) {
  isDragOver.value = false
  if (props.disabled) return
  const dt = event.dataTransfer
  if (dt?.files.length) addFiles(dt.files)
}

function onFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.length) addFiles(input.files)
  input.value = ''
}

function triggerFileInput() {
  if (!props.disabled) fileInput.value?.click()
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const fileIcon = (mime: string) => {
  if (mime.startsWith('image/')) return Image
  if (mime.includes('pdf')) return FileText
  return File
}
</script>

<template>
  <div class="space-y-2">
    <label v-if="label" class="block text-sm font-medium text-gray-700">{{ label }}</label>
    <p v-if="description" class="text-sm text-gray-400">{{ description }}</p>

    <div
      ref="dropZoneRef"
      @dragenter.prevent="isDragOver = true"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
      :class="[
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
        isDragOver ? 'border-primary-400 bg-primary-50' : error ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50',
        disabled ? 'opacity-50 cursor-not-allowed' : '',
      ]"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        class="hidden"
        @change="onFileSelect"
      />
      <Upload class="w-10 h-10 text-gray-300 mx-auto mb-3" />
      <p class="text-sm font-medium text-gray-600">
        Arrastra archivos aquí o <span class="text-primary-600">selecciona</span>
      </p>
      <p class="text-xs text-gray-400 mt-1">
        {{ accept.replace(/,/g, ', ') }} — máx {{ (maxSize / 1024 / 1024).toFixed(0) }}MB
      </p>
    </div>

    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

    <div v-if="files.length" class="space-y-2 mt-3">
      <div
        v-for="file in files"
        :key="file.id"
        class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
      >
        <div v-if="file.preview" class="w-10 h-10 rounded-lg overflow-hidden shrink-0 bg-gray-200">
          <img :src="file.preview" :alt="file.file.name" class="w-full h-full object-cover" />
        </div>
        <component :is="fileIcon(file.file.type)" v-else class="w-8 h-8 text-gray-400 shrink-0" />
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ file.file.name }}</p>
          <p class="text-xs text-gray-400">{{ formatSize(file.file.size) }}</p>
          <p v-if="file.error" class="text-xs text-red-500">{{ file.error }}</p>
        </div>
        <button
          @click.stop="removeFile(file)"
          class="p-1 text-gray-400 hover:text-red-500 transition-colors shrink-0"
          aria-label="Eliminar archivo"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
