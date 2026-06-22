<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Tours</h1>
        <p class="text-gray-500 mt-1">Crear, editar y administrar experiencias turísticas</p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
      >
        <Plus class="w-4 h-4" />
        <span>Nuevo Tour</span>
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Total Tours</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Activos</p>
        <p class="text-2xl font-bold text-green-600">{{ stats.active }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Destacados</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.featured }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Categorías</p>
        <p class="text-2xl font-bold text-amber-600">{{ stats.categories }}</p>
      </UiCard>
    </div>

    <!-- Filters -->
    <UiCard padding="xs">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input v-model="filters.search" type="text" placeholder="Nombre o descripción..." class="w-full px-3 py-2 border border-gray-300 rounded-lg" @input="debouncedSearch">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
          <UiSelect v-model="filters.category" :options="categoryOptions" placeholder="Todas" @update:model-value="page = 1; loadTours()" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Dificultad</label>
          <UiSelect v-model="filters.difficulty" :options="difficultyOptions" placeholder="Todas" @update:model-value="page = 1; loadTours()" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <UiSelect v-model="filters.status" :options="statusOptions" placeholder="Todos" @update:model-value="page = 1; loadTours()" />
        </div>
      </div>
    </UiCard>

    <!-- Tours Table -->
    <UiCard padding="none" class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tour</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoría</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duración</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dificultad</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precio</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="tour in tours" :key="tour.id" class="hover:bg-gray-50">
              <td class="px-4 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-100 to-emerald-100 flex items-center justify-center text-lg">
                    {{ categoryIcon(tour.category) }}
                  </div>
                  <div>
                    <div class="flex items-center gap-2">
                      <p class="font-medium text-gray-900">{{ tour.name }}</p>
                      <span v-if="tour.is_featured" class="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">⭐</span>
                    </div>
                    <p class="text-xs text-gray-500">{{ tour.location }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <UiBadge>{{ tour.category }}</UiBadge>
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                {{ tour.duration_hours }}h
              </td>
              <td class="px-4 py-4">
                <UiBadge :variant="difficultyVariant(tour.difficulty)">{{ tour.difficulty }}</UiBadge>
              </td>
              <td class="px-4 py-4 text-sm font-medium text-gray-900">
                ${{ tour.price }}
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                {{ tour.rating ? '⭐ ' + tour.rating.toFixed(1) : '—' }}
              </td>
              <td class="px-4 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="toggleFeatured(tour)" class="p-2 text-purple-600 hover:bg-purple-50 rounded-lg" :title="tour.is_featured ? 'Quitar destacado' : 'Destacar'">
                    {{ tour.is_featured ? '💔' : '⭐' }}
                  </button>
                  <button @click="editTour(tour)" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg" title="Editar">
                    <Edit class="w-4 h-4" />
                  </button>
                  <button @click="confirmDelete(tour)" class="p-2 text-red-600 hover:bg-red-50 rounded-lg" title="Desactivar">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty state -->
      <div v-if="!loading && tours.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-lg font-medium mb-2">No hay tours aún</p>
        <p class="text-sm">Creá el primer tour usando el botón "Nuevo Tour"</p>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="flex items-center justify-between p-4 border-t border-gray-100">
        <p class="text-sm text-gray-500">Mostrando {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} de {{ total }}</p>
        <div class="flex gap-1">
          <button :disabled="page <= 1" class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed" @click="changePage(page - 1)">Anterior</button>
          <button v-for="p in totalPages" :key="p" :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-primary-600 text-white' : 'border border-gray-200 hover:bg-gray-50']" @click="changePage(p)">{{ p }}</button>
          <button :disabled="page >= totalPages" class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed" @click="changePage(page + 1)">Siguiente</button>
        </div>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-8">
        <div class="flex flex-col items-center gap-2">
          <UiSpinner size="md" color="primary" />
          <span class="text-sm text-gray-500">Cargando...</span>
        </div>
      </div>
    </UiCard>

    <!-- Create/Edit Modal -->
    <UiModal v-model="showModal" :title="editingTour ? 'Editar Tour' : 'Nuevo Tour'" max-width="max-w-3xl" @update:model-value="!showModal && (editingTour = null)">
      <form @submit.prevent="saveTour" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
            <input v-model="form.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Ej: Rafting Pacuare">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ubicación *</label>
            <input v-model="form.location" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Ej: Pacuare, Turrialba">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Categoría *</label>
            <select v-model="form.category" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Seleccionar...</option>
              <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Dificultad</label>
            <select v-model="form.difficulty" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="easy">Fácil</option>
              <option value="moderate">Moderada</option>
              <option value="hard">Difícil</option>
              <option value="extreme">Extrema</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio (USD) *</label>
            <input v-model.number="form.price" type="number" min="0" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="99">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Duración (horas) *</label>
            <input v-model.number="form.duration_hours" type="number" min="0.5" step="0.5" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="4">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Grupo máximo</label>
            <input v-model.number="form.max_group_size" type="number" min="1" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="20">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Punto de encuentro</label>
            <input v-model="form.meeting_point" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Oficina principal">
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
          <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Descripción del tour..."></textarea>
        </div>
        <div class="flex items-center gap-6">
          <label class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300">
            <span class="text-sm text-gray-700">Activo</span>
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.is_featured" type="checkbox" class="rounded border-gray-300">
            <span class="text-sm text-gray-700">Destacado</span>
          </label>
        </div>
        <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
          <button type="button" @click="showModal = false; editingTour = null" class="px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50">Cancelar</button>
          <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2">
            <UiSpinner v-if="saving" size="sm" color="white" />
            {{ editingTour ? 'Guardar Cambios' : 'Crear Tour' }}
          </button>
        </div>
      </form>
    </UiModal>

    <!-- Confirm Dialog -->
    <UiConfirmDialog v-model="showConfirm" :title="confirmTitle" :message="confirmMessage" :confirm-text="confirmConfirmText" :variant="confirmVariant" :loading="confirmLoading" @confirm="executeConfirmAction" />
  </div>
</template>

<script setup lang="ts">
import { Plus, Edit, Trash2 } from 'lucide-vue-next'

definePageMeta({ layout: 'superadmin', middleware: ['superadmin'] })

const api = useApi()
const toast = useToast()

const tours = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingTour = ref<any>(null)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const stats = ref({ total: 0, active: 0, featured: 0, categories: 0 })

const filters = ref({ search: '', category: '', difficulty: '', status: 'all' })

const categoryOptions = [
  { value: 'adventure', label: 'Aventura' },
  { value: 'nature', label: 'Naturaleza' },
  { value: 'cultural', label: 'Cultural' },
  { value: 'wildlife', label: 'Wildlife' },
  { value: 'gastronomic', label: 'Gastronómico' },
  { value: 'beach', label: 'Playa' },
]

const difficultyOptions = [
  { value: '', label: 'Todas' },
  { value: 'easy', label: 'Fácil' },
  { value: 'moderate', label: 'Moderada' },
  { value: 'hard', label: 'Difícil' },
  { value: 'extreme', label: 'Extrema' },
]

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'active', label: 'Activos' },
  { value: 'inactive', label: 'Inactivos' },
]

const form = reactive({
  name: '',
  description: '',
  category: '',
  location: '',
  difficulty: 'easy',
  price: 0,
  duration_hours: 4,
  max_group_size: 20,
  meeting_point: '',
  is_active: true,
  is_featured: false,
})

function resetForm() {
  form.name = ''
  form.description = ''
  form.category = ''
  form.location = ''
  form.difficulty = 'easy'
  form.price = 0
  form.duration_hours = 4
  form.max_group_size = 20
  form.meeting_point = ''
  form.is_active = true
  form.is_featured = false
}

function categoryIcon(cat: string): string {
  const icons: Record<string, string> = { adventure: '🚣', nature: '🌿', cultural: '🏛️', wildlife: '🦥', gastronomic: '🍜', beach: '🏖️' }
  return icons[cat] || '🎯'
}

function difficultyVariant(d: string): string {
  const variants: Record<string, string> = { easy: 'success', moderate: 'warning', hard: 'danger', extreme: 'danger' }
  return variants[d] || 'info'
}

let searchTimeout: NodeJS.Timeout
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { page.value = 1; loadTours() }, 400)
}

async function loadTours() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filters.value.search) params.q = filters.value.search
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.difficulty) params.difficulty = filters.value.difficulty

    const data = await api.get<any>('/tours', params)
    tours.value = data.items || []
    total.value = data.total || 0

    stats.value = {
      total: data.total || 0,
      active: (data.items || []).filter((t: any) => t.is_active !== false).length,
      featured: (data.items || []).filter((t: any) => t.is_featured).length,
      categories: new Set((data.items || []).map((t: any) => t.category)).size,
    }
  } catch (e: any) {
    toast.error('Error al cargar tours')
  } finally {
    loading.value = false
  }
}

function changePage(p: number) {
  page.value = p
  loadTours()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openCreateModal() {
  editingTour.value = null
  resetForm()
  showModal.value = true
}

function editTour(tour: any) {
  editingTour.value = tour
  form.name = tour.name
  form.description = tour.description || ''
  form.category = tour.category || ''
  form.location = tour.location || ''
  form.difficulty = tour.difficulty || 'easy'
  form.price = tour.price || 0
  form.duration_hours = tour.duration_hours || 4
  form.max_group_size = tour.max_group_size || 20
  form.meeting_point = tour.meeting_point || ''
  form.is_active = tour.is_active !== false
  form.is_featured = tour.is_featured || false
  showModal.value = true
}

async function saveTour() {
  saving.value = true
  try {
    const body = {
      name: form.name,
      description: form.description || null,
      category: form.category,
      location: form.location,
      difficulty: form.difficulty,
      price: form.price,
      duration_hours: form.duration_hours,
      max_group_size: form.max_group_size,
      meeting_point: form.meeting_point || null,
    }

    if (editingTour.value) {
      await api.put(`/tours/${editingTour.value.id}`, { ...body, is_active: form.is_active, is_featured: form.is_featured })
      toast.success('Tour actualizado')
    } else {
      await api.post('/tours', body)
      toast.success('Tour creado')
    }

    showModal.value = false
    editingTour.value = null
    loadTours()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al guardar tour')
  } finally {
    saving.value = false
  }
}

async function toggleFeatured(tour: any) {
  try {
    await api.put(`/tours/${tour.id}`, { is_featured: !tour.is_featured })
    tour.is_featured = !tour.is_featured
    toast.success(tour.is_featured ? 'Tour destacado' : 'Destacado quitado')
  } catch { toast.error('Error al cambiar destacado') }
}

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

function openConfirm(title: string, message: string, action: () => Promise<void>, options?: { confirmText?: string; variant?: 'danger' | 'warning' | 'info' }) {
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

function confirmDelete(tour: any) {
  openConfirm(
    'Desactivar Tour',
    `¿Estás seguro de desactivar "${tour.name}"? No se eliminará permanentemente pero dejará de mostrarse en la web.`,
    async () => {
      try {
        await api.put(`/tours/${tour.id}`, { is_active: false })
        toast.success('Tour desactivado')
        loadTours()
      } catch { toast.error('Error al desactivar tour') }
    },
    { confirmText: 'Desactivar', variant: 'danger' }
  )
}

onMounted(loadTours)
</script>
