<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin'],
})

const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()
const vendorId = route.params.id as string

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const loading = ref(true)
const error = ref('')
const vendor = ref<any>(null)
const showApproveModal = ref(false)
const approveAction = ref<'approve' | 'reject' | 'suspend' | 'reactivate'>('approve')
const approveReason = ref('')

const goBack = () => router.push('/superadmin/vendors')

async function loadVendor() {
  loading.value = true
  try {
    vendor.value = await api.get(`/superadmin/vendors/${vendorId}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar vendor'
  } finally {
    loading.value = false
  }
}

async function toggleFeatured() {
  try {
    await api.post(`/superadmin/vendors/${vendorId}/feature`, {
      featured: !vendor.value.is_featured,
    })
    vendor.value.is_featured = !vendor.value.is_featured
    toast.success(vendor.value.is_featured ? 'Vendor destacado' : 'Vendor no destacado')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al cambiar destacado')
  }
}

function openApproval(action: 'approve' | 'reject' | 'suspend' | 'reactivate') {
  approveAction.value = action
  approveReason.value = ''
  showApproveModal.value = true
}

async function submitApproval() {
  try {
    await api.post(`/superadmin/vendors/${vendorId}/approval`, {
      action: approveAction.value,
      reason: approveReason.value || `${approveAction.value} by Super Admin`,
    })
    toast.success(`Vendor ${approveAction.value === 'approve' ? 'aprobado' : approveAction.value === 'reject' ? 'rechazado' : approveAction.value === 'suspend' ? 'suspendido' : 'reactivado'} exitosamente`)
    showApproveModal.value = false
    await loadVendor()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al procesar solicitud')
  }
}

const statusBadgeVariant = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    active: 'success',
    suspended: 'danger',
    rejected: 'default',
  }
  return map[status] || 'default'
}

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    pending: 'Pendiente',
    active: 'Activo',
    suspended: 'Suspendido',
    rejected: 'Rechazado',
  }
  return map[status] || status
}

onMounted(async () => {
  if (!UUID_REGEX.test(route.params.id as string)) {
    await router.replace('/superadmin/vendors')
    return
  }
  await loadVendor()
})
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-24">
    <UiSpinner size="md" color="primary" />
  </div>

  <div v-else-if="error" class="text-center py-24">
    <p class="text-red-500 text-lg">{{ error }}</p>
    <button @click="goBack" class="mt-4 text-blue-600 hover:text-blue-800">&larr; Volver</button>
  </div>

  <div v-else-if="vendor" class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button @click="goBack" class="p-2 hover:bg-gray-100 rounded-lg">
          <span class="text-2xl">&larr;</span>
        </button>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ vendor.business_name }}</h1>
          <p class="text-gray-500">{{ vendor.business_type }}</p>
        </div>
      </div>
      <div class="flex gap-3">
        <NuxtLink
          :to="`/superadmin/vendors/${vendorId}/documents`"
          class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Documentos
        </NuxtLink>
        <button
          @click="toggleFeatured"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          {{ vendor.is_featured ? 'Quitar Destacado' : 'Destacar' }}
        </button>
      </div>
    </div>

    <!-- Info Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Business Info -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Informaci&oacute;n del Negocio</h2>
        <dl class="space-y-3">
          <div class="flex justify-between">
            <dt class="text-gray-500">Estado</dt>
            <dd>
              <UiBadge :variant="statusBadgeVariant(vendor.status)">{{ formatStatus(vendor.status) }}</UiBadge>
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Tipo</dt>
            <dd class="font-medium text-gray-900">{{ vendor.business_type }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Rating</dt>
            <dd class="font-medium text-gray-900">{{ vendor.rating || 0 }} / 5</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Comisi&oacute;n</dt>
            <dd class="font-medium text-gray-900">{{ vendor.commission_rate }}%</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Destacado</dt>
            <dd>
              <span :class="vendor.is_featured ? 'text-purple-600' : 'text-gray-400'">{{ vendor.is_featured ? 'S&iacute;' : 'No' }}</span>
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Registrado</dt>
            <dd class="font-medium text-gray-900">{{ vendor.created_at?.slice(0, 10) }}</dd>
          </div>
        </dl>
      </div>

      <!-- Owner Info -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Datos del Propietario</h2>
        <dl v-if="vendor.owner_email" class="space-y-3">
          <div class="flex justify-between">
            <dt class="text-gray-500">Nombre</dt>
            <dd class="font-medium text-gray-900">{{ vendor.owner_name || 'N/A' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Email</dt>
            <dd class="font-medium text-gray-900">{{ vendor.owner_email }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Tel&eacute;fono</dt>
            <dd class="font-medium text-gray-900">{{ vendor.owner_phone || 'N/A' }}</dd>
          </div>
        </dl>
        <p v-else class="text-gray-400 text-sm">Sin propietario asignado</p>
      </div>

      <!-- Stats -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Estad&iacute;sticas</h2>
        <dl class="space-y-3">
          <div class="flex justify-between">
            <dt class="text-gray-500">Reservas</dt>
            <dd class="font-medium text-gray-900">{{ vendor.stats?.total_bookings || 0 }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Ingresos</dt>
            <dd class="font-medium text-gray-900">${{ (vendor.stats?.total_revenue || 0).toLocaleString() }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Completadas</dt>
            <dd class="font-medium text-green-600">{{ vendor.stats?.completed_bookings || 0 }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Canceladas</dt>
            <dd class="font-medium text-red-600">{{ vendor.stats?.cancelled_bookings || 0 }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Propiedades</dt>
            <dd class="font-medium text-gray-900">{{ vendor.stats?.total_properties || 0 }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Reviews</dt>
            <dd class="font-medium text-gray-900">{{ vendor.stats?.total_reviews || 0 }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <!-- Actions -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Acciones</h2>
      <div v-if="vendor.status === 'pending'" class="flex gap-3">
        <button @click="openApproval('approve')" class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          Aprobar
        </button>
        <button @click="openApproval('reject')" class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
          Rechazar
        </button>
      </div>
      <div v-else-if="vendor.status === 'active'" class="flex gap-3">
        <button @click="openApproval('suspend')" class="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
          Suspender
        </button>
      </div>
      <div v-else-if="vendor.status === 'suspended'" class="flex gap-3">
        <button @click="openApproval('reactivate')" class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          Reactivar
        </button>
      </div>
      <p v-else class="text-gray-400 text-sm">No hay acciones disponibles para este estado.</p>
    </div>

    <!-- Compliance Flags -->
    <div v-if="vendor.compliance_flags && vendor.compliance_flags.length > 0" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Alertas de Cumplimiento</h2>
      <div class="space-y-2">
        <div v-for="(flag, i) in vendor.compliance_flags" :key="i" class="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
          <span class="text-yellow-600 text-xl">&Warning;</span>
          <span class="text-sm text-yellow-800">{{ flag }}</span>
        </div>
      </div>
    </div>

    <!-- Approval Modal -->
    <UiModal v-if="showApproveModal" v-model="showApproveModal" :title="'Confirmar ' + (approveAction === 'approve' ? 'Aprobaci&oacute;n' : approveAction === 'reject' ? 'Rechazo' : approveAction === 'suspend' ? 'Suspensi&oacute;n' : 'Reactivaci&oacute;n')" max-width="max-w-md">
      <div class="space-y-4">
        <p class="text-gray-600">
          {{ approveAction === 'approve' ? '&iquest;Est&aacute;s seguro de aprobar este vendor?' : approveAction === 'reject' ? '&iquest;Est&aacute;s seguro de rechazar este vendor?' : approveAction === 'suspend' ? '&iquest;Est&aacute;s seguro de suspender este vendor?' : '&iquest;Est&aacute;s seguro de reactivar este vendor?' }}
        </p>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Raz&oacute;n</label>
          <textarea v-model="approveReason" class="w-full px-4 py-2.5 border border-gray-300 rounded-xl resize-none" rows="3" placeholder="Opcional"></textarea>
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="showApproveModal = false" class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
            Cancelar
          </button>
          <button @click="submitApproval" :class="approveAction === 'reject' ? 'bg-red-600 hover:bg-red-700' : 'bg-slate-900 hover:bg-slate-800'" class="px-6 py-2 text-white rounded-lg transition-colors">
            Confirmar
          </button>
        </div>
      </div>
    </UiModal>
  </div>
</template>
