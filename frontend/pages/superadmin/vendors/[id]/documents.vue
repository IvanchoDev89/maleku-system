<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const route = useRoute()
const router = useRouter()
const api = useApi()
const vendorId = route.params.id as string

const vendor = ref<any>(null)
const loading = ref(true)
const error = ref('')

const fetchVendor = async () => {
  loading.value = true
  error.value = ''
  try {
    vendor.value = await api.get(`/superadmin/vendors/${vendorId}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar proveedor'
    console.error('Error fetching vendor:', e)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/superadmin/vendors')
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  suspended: 'bg-gray-100 text-gray-800',
}

const statusLabels: Record<string, string> = {
  pending: 'Pendiente',
  active: 'Activo',
  rejected: 'Rechazado',
  suspended: 'Suspendido',
}

onMounted(() => {
  fetchVendor()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button @click="goBack" class="p-2 hover:bg-gray-100 rounded-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Documentos del Proveedor</h1>
          <p class="text-gray-500" v-if="vendor">{{ vendor.business_name }}</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500">Cargando proveedor...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-red-500 text-lg">{{ error }}</p>
      <button @click="fetchVendor" class="mt-4 text-primary-600 hover:text-primary-700 font-medium">Reintentar</button>
    </div>

    <!-- Vendor Details -->
    <template v-else-if="vendor">
      <!-- Vendor Info Card -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Informacion del Proveedor</h3>
            <dl class="space-y-3">
              <div class="flex justify-between">
                <dt class="text-gray-500">Nombre:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.business_name }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Tipo:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.business_type }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Email:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.owner_email }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Propietario:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.owner_name }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Estado:</dt>
                <dd>
                  <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[vendor.status] || 'bg-gray-100']">
                    {{ statusLabels[vendor.status] || vendor.status }}
                  </span>
                </dd>
              </div>
            </dl>
          </div>
          <div>
            <h3 class="text-lg font-medium text-gray-900 mb-4">Estadisticas</h3>
            <dl class="space-y-3" v-if="vendor.stats">
              <div class="flex justify-between">
                <dt class="text-gray-500">Reservas totales:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.stats.total_bookings || 0 }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Ingresos totales:</dt>
                <dd class="font-medium text-gray-900">${{ (vendor.stats.total_revenue || 0).toLocaleString() }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Propiedades:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.stats.total_properties || 0 }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Rating:</dt>
                <dd class="font-medium text-gray-900">{{ vendor.rating || 0 }} / 5</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <!-- Compliance Flags -->
      <div class="bg-white rounded-lg shadow p-6" v-if="vendor.compliance_flags && vendor.compliance_flags.length > 0">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Alertas de Cumplimiento</h3>
        <div class="space-y-2">
          <div v-for="(flag, i) in vendor.compliance_flags" :key="i" class="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
            <span class="text-yellow-600">⚠</span>
            <span class="text-sm text-yellow-800">{{ flag }}</span>
          </div>
        </div>
      </div>

      <!-- Document Verification Status -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Estado de Verificacion</h3>
        <div class="flex items-center gap-4">
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-gray-500">Documentos verificados:</span>
              <span class="text-sm font-medium" :class="vendor.documents_verified ? 'text-green-600' : 'text-yellow-600'">
                {{ vendor.documents_verified ? 'Completado' : 'Pendiente' }}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="h-2.5 rounded-full transition-all duration-300" :class="vendor.documents_verified ? 'bg-green-600' : 'bg-yellow-400'" :style="{ width: vendor.documents_verified ? '100%' : '50%' }"></div>
            </div>
          </div>
        </div>
        <p class="mt-4 text-sm text-gray-500">
          La verificacion de documentos individuales estara disponible proximamente.
        </p>
      </div>

      <!-- Back button -->
      <div class="flex justify-end">
        <button @click="goBack" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700">
          Volver a Proveedores
        </button>
      </div>
    </template>
  </div>
</template>
