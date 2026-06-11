<template>
  <form @submit.prevent="handleSubmit" class="bg-white rounded-xl shadow-sm p-6 max-w-3xl">
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Cargando...</p>
    </div>

    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
          <input v-model="form.name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Categoría *</label>
          <UiSelect v-model="form.category" :options="tourCategoryOptions" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Dificultad</label>
          <UiSelect v-model="form.difficulty" :options="difficultyOptions" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Duración (horas) *</label>
          <input v-model.number="form.duration_hours" type="number" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Duración texto</label>
          <input v-model="form.duration_text" type="text" placeholder="e.g. 4-5 horas" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
          <input v-model="form.location" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Punto de Encuentro</label>
          <input v-model="form.meeting_point" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Precio ($) *</label>
          <input v-model.number="form.price" type="number" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Moneda</label>
          <UiSelect v-model="form.currency" :options="currencyOptions" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tamaño máximo grupo</label>
          <input v-model.number="form.max_group_size" type="number" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Edad mínima</label>
          <input v-model.number="form.min_age" type="number" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
          <input v-model="form.slug" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
          <textarea v-model="form.description" rows="4" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
        </div>

        <div v-if="isEditing" class="md:col-span-2">
          <label class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" class="w-4 h-4 text-primary" />
            <span class="text-sm font-medium text-gray-700">Tour activo</span>
          </label>
        </div>
      </div>

      <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {{ error }}
      </div>

      <div class="mt-6 flex gap-4">
        <button type="submit" :disabled="saving" class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50">
          {{ saving ? 'Guardando...' : isEditing ? 'Guardar Cambios' : 'Guardar Tour' }}
        </button>
        <NuxtLink :to="cancelUrl || '/vendor/tours'" class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
          Cancelar
        </NuxtLink>
      </div>
    </template>
  </form>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

const props = defineProps<{
  tourId?: string
  cancelUrl?: string
}>()

const router = useRouter()
const api = useApi()
const isEditing = computed(() => !!props.tourId)

const tourCategoryOptions = [
  { value: 'adventure', label: 'Aventura' },
  { value: 'nature', label: 'Naturaleza' },
  { value: 'cultural', label: 'Cultural' },
  { value: 'water', label: 'Acuático' },
  { value: 'wellness', label: 'Bienestar' },
  { value: 'gastronomy', label: 'Gastronomía' },
]

const difficultyOptions = [
  { value: 'easy', label: 'Fácil' },
  { value: 'moderate', label: 'Moderada' },
  { value: 'challenging', label: 'Desafiante' },
]

const currencyOptions = [
  { value: 'USD', label: 'USD' },
  { value: 'EUR', label: 'EUR' },
  { value: 'CRC', label: 'CRC' },
]

const loading = ref(false)
const saving = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  slug: '',
  description: '',
  category: 'adventure',
  difficulty: 'easy',
  duration_hours: 4,
  duration_text: '',
  location: '',
  meeting_point: '',
  price: 0,
  currency: 'USD',
  max_group_size: 15,
  min_age: 0,
  is_active: true,
})

const generateSlug = () => {
  form.slug = form.name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

watch(() => form.name, generateSlug)

const loadTour = async () => {
  if (!props.tourId) return
  loading.value = true
  try {
    const data = await api.get<any>(`/tours/${props.tourId}`)
    Object.assign(form, data)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar tour'
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  saving.value = true
  error.value = ''
  try {
    if (isEditing.value) {
      await api.put(`/tours/${props.tourId}`, form)
    } else {
      await api.post('/tours', form)
    }
    router.push('/vendor/tours')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar tour'
  } finally {
    saving.value = false
  }
}

onMounted(loadTour)
</script>
