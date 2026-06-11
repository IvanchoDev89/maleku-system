<template>
  <div v-if="loading" class="flex items-center justify-center p-12">
    <div class="flex items-center gap-3">
      <svg class="animate-spin h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-gray-500">Cargando...</span>
    </div>
  </div>
  
  <div v-else-if="!vendor" class="text-center p-12">
    <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
      <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-1 4h1M5 3h1m-1 4h1m4-4h1m-1 4h1m-1 4h1" />
      </svg>
    </div>
    <h2 class="text-xl font-bold text-gray-900 mb-2">Proveedor no encontrado</h2>
    <p class="text-gray-500 mb-6">El proveedor que buscas no existe o ha sido eliminado.</p>
    <NuxtLink to="/admin/vendors" class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-700">
      Volver a Proveedores
    </NuxtLink>
  </div>
  
  <div v-else class="space-y-6">
    <div class="flex items-center justify-between">
      <NuxtLink to="/admin/vendors" class="flex items-center gap-2 text-gray-500 hover:text-gray-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Volver a Proveedores
      </NuxtLink>
      
      <div class="flex gap-2">
        <button 
          @click="toggleVerified"
          class="px-4 py-2 rounded-lg flex items-center gap-2"
          :class="vendor.is_verified ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
        >
          <svg v-if="vendor.is_verified" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ vendor.is_verified ? 'Verificado' : 'Marcar Verificado' }}
        </button>
        
        <button 
          @click="toggleActive"
          class="px-4 py-2 rounded-lg flex items-center gap-2"
          :class="vendor.is_active ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' : 'bg-red-100 text-red-700 hover:bg-red-200'"
        >
          <span class="w-2 h-2 rounded-full" :class="vendor.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
          {{ vendor.is_active ? 'Activo' : 'Inactivo' }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div class="flex items-start gap-4">
            <div class="w-20 h-20 bg-primary/10 rounded-2xl flex items-center justify-center text-primary font-bold text-2xl overflow-hidden flex-shrink-0">
              <NuxtImg v-if="vendor.logo_url" :src="vendor.logo_url" :alt="vendor.business_name" class="w-full h-full object-cover" width="80" height="80" format="webp" />
              <span v-else>{{ vendor.business_name.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-1">
                <h1 class="text-2xl font-bold text-gray-900">{{ vendor.business_name }}</h1>
                <span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                  {{ getBusinessTypeLabel(vendor.business_type) }}
                </span>
              </div>
              <p class="text-gray-500">/{{ vendor.business_slug }}</p>
              <div class="flex items-center gap-4 mt-2">
                <div v-if="vendor.rating" class="flex items-center gap-1">
                  <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span class="font-bold">{{ vendor.rating.toFixed(1) }}</span>
                  <span class="text-gray-500">({{ vendor.total_reviews }} reseñas)</span>
                </div>
                <span v-else class="text-gray-400">Sin rating</span>
              </div>
            </div>
          </div>
          
          <div v-if="vendor.description" class="mt-6 pt-6 border-t border-gray-100">
            <h3 class="font-semibold text-gray-900 mb-2">Descripción</h3>
            <p class="text-gray-600">{{ vendor.description }}</p>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-900 mb-4">Información de Contacto</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <p class="text-xs text-gray-500">Email</p>
                <p class="text-gray-900">{{ vendor.email || 'No disponible' }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              <div>
                <p class="text-xs text-gray-500">Teléfono</p>
                <p class="text-gray-900">{{ vendor.phone || 'No disponible' }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.999 1.999 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <p class="text-xs text-gray-500">Dirección</p>
                <p class="text-gray-900">{{ vendor.address || 'No disponible' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-900 mb-4">Propietario</h3>
          <div v-if="vendor.owner" class="space-y-3">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-primary font-bold">
                {{ vendor.owner.full_name?.charAt(0).toUpperCase() || '?' }}
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ vendor.owner.full_name || 'Sin nombre' }}</p>
                <p class="text-sm text-gray-500">{{ vendor.owner.email }}</p>
              </div>
            </div>
            <div class="pt-3 border-t border-gray-100">
              <div class="flex items-center gap-2 text-sm">
                <span class="w-2 h-2 rounded-full" :class="vendor.owner.is_active ? 'bg-green-500' : 'bg-red-400'"></span>
                <span class="text-gray-600">{{ vendor.owner.is_active ? 'Cuenta activa' : 'Cuenta inactiva' }}</span>
              </div>
              <div class="flex items-center gap-2 text-sm mt-1">
                <svg v-if="vendor.owner.is_verified" class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-600">{{ vendor.owner.is_verified ? 'Verificado' : 'Pendiente de verificación' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-gray-500">
            Propietario no asignado
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 class="font-semibold text-gray-900 mb-4">Estadísticas</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Comisión</span>
              <span class="font-semibold text-gray-900">{{ (vendor.commission_rate * 100).toFixed(0) }}%</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-gray-600">Stripe Conectado</span>
              <span class="px-2 py-1 rounded-full text-xs font-medium" :class="vendor.stripe_connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'">
                {{ vendor.stripe_connected ? 'Sí' : 'No' }}
              </span>
            </div>
            <div class="pt-4 border-t border-gray-100">
              <p class="text-xs text-gray-500">Registrado el {{ formatDate(vendor.created_at) }}</p>
              <p class="text-xs text-gray-500">Última actualización {{ formatDate(vendor.updated_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const api = useApi()

definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const vendor = ref<any>(null)
const loading = ref(true)

const getBusinessTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    hotel: 'Hotel',
    tour_operator: 'Tour Operador',
    restaurant: 'Restaurante',
    transporter: 'Transporte',
    activity: 'Actividad'
  }
  return labels[type] || type
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchVendor = async () => {
  loading.value = true
  try {
    const vendorId = route.params.id
    vendor.value = await api.get(`/admin/vendors/${vendorId}`)
  } catch (error) {
    console.error('Error fetching vendor:', error)
    vendor.value = null
  } finally {
    loading.value = false
  }
}

const toggleVerified = async () => {
  try {
    await api.put(`/admin/vendors/${vendor.value.id}/verify`, { is_verified: !vendor.value.is_verified })
    vendor.value.is_verified = !vendor.value.is_verified
  } catch (error) {
    console.error('Error toggling verified:', error)
  }
}

const toggleActive = async () => {
  try {
    await api.put(`/admin/vendors/${vendor.value.id}/active`, { is_active: !vendor.value.is_active })
    vendor.value.is_active = !vendor.value.is_active
  } catch (error) {
    console.error('Error toggling active:', error)
  }
}

onMounted(() => {
  fetchVendor()
})
</script>