<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Mis Tours</h1>
        <p class="text-gray-500">Gestiona tus tours y experiencias</p>
      </div>
      <NuxtLink to="/vendor/tours/new" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark">
        + Nuevo Tour
      </NuxtLink>
    </div>

    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
      {{ error }}
      <button @click="fetchTours" class="ml-3 underline hover:no-underline">Reintentar</button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-8 space-y-4">
        <div v-for="i in 5" :key="i" class="flex gap-4 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-40" />
          <div class="h-4 bg-gray-200 rounded w-24" />
          <div class="h-4 bg-gray-200 rounded w-16" />
          <div class="h-4 bg-gray-200 rounded w-32" />
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-24" />
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Nombre</th>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Categoría</th>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Duración</th>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Ubicación</th>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Precio</th>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
            <th class="text-left py-3 px-4 font-semibold text-gray-600">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="tours.length === 0">
            <td colspan="7" class="text-center py-12 text-gray-500">
              No tienes tours aún.
              <NuxtLink to="/vendor/tours/new" class="text-primary hover:underline">Crear primer tour</NuxtLink>
            </td>
          </tr>
          <tr 
            v-for="tour in tours" 
            :key="tour.id"
            class="border-t hover:bg-gray-50"
          >
            <td class="py-3 px-4">
              <div class="font-medium">{{ tour.name }}</div>
              <div class="text-sm text-gray-500">{{ tour.slug }}</div>
            </td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 bg-gray-100 rounded text-sm">{{ tour.category }}</span>
            </td>
            <td class="py-3 px-4">
              {{ tour.duration_hours }}h
            </td>
            <td class="py-3 px-4 text-sm">
              {{ tour.location }}
            </td>
            <td class="py-3 px-4 font-semibold">
              ${{ tour.price }}
            </td>
            <td class="py-3 px-4">
              <UiBadge :variant="tour.is_active ? 'success' : 'danger'">
                {{ tour.is_active ? 'Activo' : 'Inactivo' }}
              </UiBadge>
            </td>
            <td class="py-3 px-4">
              <NuxtLink :to="`/vendor/tours/${tour.id}`" class="text-primary hover:underline mr-3">
                Editar
              </NuxtLink>
              <button @click="openDeleteDialog(tour)" class="text-red-600 hover:underline">
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="flex items-center justify-between mt-4">
      <p class="text-sm text-gray-500">
        Mostrando {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} de {{ total }}
      </p>
      <div class="flex gap-1">
        <button
          :disabled="page <= 1"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="changePage(page - 1)"
        >Anterior</button>
        <button
          v-for="p in totalPages"
          :key="p"
          :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-teal-600 text-white' : 'border border-gray-200 hover:bg-gray-50']"
          @click="changePage(p)"
        >{{ p }}</button>
        <button
          :disabled="page >= totalPages"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="changePage(page + 1)"
        >Siguiente</button>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <UiConfirmDialog
      :model-value="!!tourToDelete"
      title="Eliminar Tour"
      :message="`¿Estás seguro de eliminar ${tourToDelete?.name}?`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="tourToDelete = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const api = useApi()

const tours = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const tourToDelete = ref<any>(null)
const deleting = ref(false)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const fetchTours = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.get('/tours/vendor/my', {
      page: page.value,
      page_size: pageSize.value
    })
    tours.value = data.items || []
    total.value = data.total || tours.value.length
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar tours'
  } finally {
    loading.value = false
  }
}

const changePage = (p: number) => {
  page.value = p
  fetchTours()
}

const openDeleteDialog = (tour: any) => {
  tourToDelete.value = tour
}

const confirmDelete = async () => {
  if (!tourToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/tours/${tourToDelete.value.id}`)
    tourToDelete.value = null
    fetchTours()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al eliminar tour'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchTours()
})
</script>
