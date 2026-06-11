<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Mis Propiedades</h1>
        <p class="text-gray-500">Gestiona tus hoteles y villas</p>
      </div>
      <NuxtLink to="/vendor/properties/new" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-700">
        + Nueva Propiedad
      </NuxtLink>
    </div>

    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
      {{ error }}
      <button @click="fetchProperties" class="ml-3 underline hover:no-underline">Reintentar</button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-8 space-y-4">
        <div v-for="i in 5" :key="i" class="flex gap-4 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-40" />
          <div class="h-4 bg-gray-200 rounded w-24" />
          <div class="h-4 bg-gray-200 rounded w-32" />
          <div class="h-4 bg-gray-200 rounded w-16" />
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-24" />
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Nombre</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Tipo</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Ubicación</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Habitaciones</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="properties.length === 0">
              <td colspan="6" class="text-center py-12 text-gray-500">
                No tienes propiedades aún.
                <NuxtLink to="/vendor/properties/new" class="text-primary hover:underline">Crear primera propiedad</NuxtLink>
              </td>
            </tr>
            <tr 
              v-for="property in properties" 
              :key="property.id"
              class="border-t hover:bg-gray-50"
            >
              <td class="py-3 px-4">
                <div class="font-medium">{{ property.name }}</div>
                <div class="text-sm text-gray-500">{{ property.slug }}</div>
              </td>
              <td class="py-3 px-4 hidden sm:table-cell">
                <span class="px-2 py-1 bg-gray-100 rounded text-sm">{{ property.property_type }}</span>
              </td>
              <td class="py-3 px-4 text-sm hidden md:table-cell">
                <div>{{ property.city }}</div>
                <div class="text-gray-500">{{ property.region }}</div>
              </td>
              <td class="py-3 px-4 hidden sm:table-cell">
                {{ property.rooms?.length || 0 }}
              </td>
              <td class="py-3 px-4">
                <UiBadge :variant="property.is_active ? 'success' : 'danger'">
                  {{ property.is_active ? 'Activo' : 'Inactivo' }}
                </UiBadge>
              </td>
              <td class="py-3 px-4">
                <NuxtLink :to="`/vendor/properties/${property.id}`" class="text-primary hover:underline mr-3">
                  Editar
                </NuxtLink>
                <button @click="openDeleteDialog(property)" class="text-red-600 hover:underline">
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
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
          :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-primary-600 text-white' : 'border border-gray-200 hover:bg-gray-50']"
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
      :model-value="!!propertyToDelete"
      title="Eliminar Propiedad"
      :message="`¿Estás seguro de eliminar ${propertyToDelete?.name}?`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="propertyToDelete = null"
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

const properties = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const propertyToDelete = ref<any>(null)
const deleting = ref(false)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const fetchProperties = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.get<{ items: any[]; total: number }>('/properties/vendor/my', {
      page: page.value,
      page_size: pageSize.value
    })
    properties.value = data.items || []
    total.value = data.total || properties.value.length
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar propiedades'
  } finally {
    loading.value = false
  }
}

const changePage = (p: number) => {
  page.value = p
  fetchProperties()
}

const openDeleteDialog = (property: any) => {
  propertyToDelete.value = property
}

const confirmDelete = async () => {
  if (!propertyToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/properties/${propertyToDelete.value.id}`)
    propertyToDelete.value = null
    fetchProperties()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al eliminar propiedad'
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchProperties()
})
</script>
