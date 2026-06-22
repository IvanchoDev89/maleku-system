<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()
const vendorId = route.params.id as string

const vendor = ref<any>(null)
const loading = ref(true)
const error = ref('')
const runningCompliance = ref(false)

const fetchVendor = async () => {
  loading.value = true
  error.value = ''
  try {
    vendor.value = await api.get(`/superadmin/vendors/${vendorId}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar proveedor'
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

const runComplianceCheck = async () => {
  runningCompliance.value = true
  try {
    await api.post(`/superadmin/vendors/${vendorId}/compliance-check`, {
      check_documents: true,
      check_bookings: true,
      check_reviews: true,
    })
    toast.success('Verificación de cumplimiento completada')
    await fetchVendor()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al ejecutar verificación')
  } finally {
    runningCompliance.value = false
  }
}

const requestDocuments = async () => {
  try {
    await api.post(`/superadmin/vendors/${vendorId}/approval`, {
      action: 'request_documents',
      reason: 'Documentos requeridos para activación',
      require_documents: ['tax_id', 'business_license', 'insurance'],
    })
    toast.success('Solicitud de documentos enviada al proveedor')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al solicitar documentos')
  }
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
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando proveedor...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-red-500 text-lg">{{ error }}</p>
      <button @click="fetchVendor" class="mt-4 text-primary-600 hover:text-primary-700 font-medium">Reintentar</button>
    </div>

    <template v-else-if="vendor">
      <!-- Vendor Info Card -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">Información del Proveedor</h3>
          <span :class="['px-3 py-1 text-xs font-medium rounded-full', statusColors[vendor.status] || 'bg-gray-100']">
            {{ statusLabels[vendor.status] || vendor.status }}
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
            <div class="flex justify-between" v-if="vendor.tax_id">
              <dt class="text-gray-500">Tax ID:</dt>
              <dd class="font-medium text-gray-900">{{ vendor.tax_id }}</dd>
            </div>
          </dl>
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

      <!-- Document Checklist -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">Checklist de Documentos</h3>
          <div class="flex gap-3">
            <button
              @click="runComplianceCheck"
              :disabled="runningCompliance"
              class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 flex items-center gap-2"
            >
              <UiSpinner v-if="runningCompliance" size="sm" color="primary" />
              Verificar Cumplimiento
            </button>
            <button
              @click="requestDocuments"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
            >
              Solicitar Documentos
            </button>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span :class="vendor.tax_id ? 'text-green-600' : 'text-gray-300'">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <div>
                <p class="font-medium text-gray-900">Registro Fiscal (Tax ID)</p>
                <p class="text-sm text-gray-500">{{ vendor.tax_id || 'No proporcionado' }}</p>
              </div>
            </div>
            <span :class="vendor.tax_id ? 'text-green-600 bg-green-50 px-2 py-1 rounded text-xs font-medium' : 'text-yellow-600 bg-yellow-50 px-2 py-1 rounded text-xs font-medium'">
              {{ vendor.tax_id ? 'Verificado' : 'Pendiente' }}
            </span>
          </div>

          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span :class="vendor.commission_rate > 0 ? 'text-green-600' : 'text-gray-300'">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <div>
                <p class="font-medium text-gray-900">Contrato de Comisión</p>
                <p class="text-sm text-gray-500">Tasa: {{ (vendor.commission_rate * 100).toFixed(1) || '0' }}%</p>
              </div>
            </div>
            <span :class="vendor.commission_rate > 0 ? 'text-green-600 bg-green-50 px-2 py-1 rounded text-xs font-medium' : 'text-yellow-600 bg-yellow-50 px-2 py-1 rounded text-xs font-medium'">
              {{ vendor.commission_rate > 0 ? 'Configurado' : 'Pendiente' }}
            </span>
          </div>

          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span :class="vendor.documents_verified ? 'text-green-600' : 'text-gray-300'">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <div>
                <p class="font-medium text-gray-900">Verificación de Identidad</p>
                <p class="text-sm text-gray-500">Documentos de identidad del propietario</p>
              </div>
            </div>
            <span :class="vendor.documents_verified ? 'text-green-600 bg-green-50 px-2 py-1 rounded text-xs font-medium' : 'text-yellow-600 bg-yellow-50 px-2 py-1 rounded text-xs font-medium'">
              {{ vendor.documents_verified ? 'Verificado' : 'Pendiente' }}
            </span>
          </div>

          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span :class="vendor.stats?.total_properties > 0 ? 'text-green-600' : 'text-gray-300'">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <div>
                <p class="font-medium text-gray-900">Listado de Servicios</p>
                <p class="text-sm text-gray-500">{{ vendor.stats?.total_properties || 0 }} propiedades/publicaciones</p>
              </div>
            </div>
            <span :class="vendor.stats?.total_properties > 0 ? 'text-green-600 bg-green-50 px-2 py-1 rounded text-xs font-medium' : 'text-yellow-600 bg-yellow-50 px-2 py-1 rounded text-xs font-medium'">
              {{ vendor.stats?.total_properties > 0 ? 'Completo' : 'Sin listados' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Compliance Flags -->
      <div v-if="vendor.compliance_flags?.length > 0" class="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-400">
        <h3 class="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
          <span class="text-yellow-600">⚠</span>
          Alertas de Cumplimiento
        </h3>
        <div class="space-y-2">
          <div v-for="(flag, i) in vendor.compliance_flags" :key="i" class="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
            <span class="text-yellow-600 text-sm">•</span>
            <span class="text-sm text-yellow-800">{{ flag }}</span>
          </div>
        </div>
      </div>

      <!-- Verification Progress -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Progreso de Verificación</h3>
        <div class="flex items-center gap-4 mb-4">
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm text-gray-500">Documentos verificados:</span>
              <span class="text-sm font-medium" :class="vendor.documents_verified ? 'text-green-600' : 'text-yellow-600'">
                {{ vendor.documents_verified ? 'Completado' : 'Pendiente' }}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="h-2.5 rounded-full transition-all duration-500" :class="vendor.documents_verified ? 'bg-green-500' : 'bg-yellow-400'" :style="{ width: vendor.documents_verified ? '100%' : '35%' }"></div>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2 text-sm" v-if="vendor.last_compliance_check">
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-gray-500">Última verificación: {{ new Date(vendor.last_compliance_check).toLocaleString() }}</span>
        </div>
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
