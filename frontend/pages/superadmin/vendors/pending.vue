<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Aprobación de Proveedores</h1>
        <p class="text-gray-500 mt-1">Revisar y aprobar nuevos vendors pendientes</p>
      </div>
      <NuxtLink 
        to="/superadmin/vendors"
        class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
      >
        ← Volver a Vendors
      </NuxtLink>
    </div>

    <!-- Pending Alert -->
    <div v-if="pendingVendors.length > 0" class="bg-amber-50 border border-amber-200 rounded-xl p-4">
      <div class="flex items-center gap-3">
        <span class="text-2xl">⏳</span>
        <div>
          <p class="font-bold text-amber-800">
            {{ pendingVendors.length }} vendor{{ pendingVendors.length > 1 ? 's' : '' }} pendiente{{ pendingVendors.length > 1 ? 's' : '' }}
          </p>
          <p class="text-sm text-amber-600">
            Requieren revisión y aprobación para activar en la plataforma
          </p>
        </div>
      </div>
    </div>

    <div v-if="pendingVendors.length === 0" class="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
      <span class="text-4xl">🎉</span>
      <p class="font-bold text-green-800 mt-4">No hay vendors pendientes</p>
      <p class="text-sm text-green-600 mt-1">Todos los proveedores han sido procesados</p>
    </div>

    <!-- Pending Vendors List -->
    <div v-else class="space-y-4">
      <div 
        v-for="vendor in pendingVendors" 
        :key="vendor.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
      >
        <!-- Vendor Header -->
        <div class="p-6 border-b border-gray-100">
          <div class="flex justify-between items-start">
            <div class="flex items-start gap-4">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center text-white text-2xl">
                🏪
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900">{{ vendor.business_name }}</h3>
                <p class="text-gray-500">{{ vendor.business_type }} • Registrado {{ formatDate(vendor.created_at) }}</p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-semibold">
                    PENDIENTE
                  </span>
                  <span v-if="vendor.compliance_flags?.length > 0" class="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-semibold">
                    ⚠️ Requiere atención
                  </span>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <button 
                @click="selectedVendor = vendor; showRejectModal = true"
                class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
              >
                Rechazar
              </button>
              <button 
                @click="confirmApproveVendor(vendor)"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                ✅ Aprobar
              </button>
            </div>
          </div>
        </div>

        <!-- Vendor Details -->
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Owner Info -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span>👤</span> Información del Propietario
            </h4>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">Nombre:</span>
                <span class="font-medium">{{ vendor.owner_name }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Email:</span>
                <span class="font-medium">{{ vendor.owner_email }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Teléfono:</span>
                <span class="font-medium">{{ vendor.owner_phone || 'No proporcionado' }}</span>
              </div>
            </div>
          </div>

          <!-- Business Info -->
          <div>
            <h4 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span>🏢</span> Información del Negocio
            </h4>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500">Tipo:</span>
                <span class="font-medium capitalize">{{ vendor.business_type }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Tax ID:</span>
                <span class="font-medium">{{ vendor.tax_id || 'No proporcionado' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">Comisión:</span>
                <span class="font-medium">{{ vendor.commission_rate }}%</span>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="md:col-span-2" v-if="vendor.description">
            <h4 class="font-semibold text-gray-900 mb-3">Descripción</h4>
            <p class="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{{ vendor.description }}</p>
          </div>

          <!-- Stats -->
          <div class="md:col-span-2">
            <h4 class="font-semibold text-gray-900 mb-3">Estadísticas Iniciales</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <p class="text-2xl font-bold text-gray-900">{{ vendor.stats?.total_bookings || 0 }}</p>
                <p class="text-xs text-gray-500">Reservas</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <p class="text-2xl font-bold text-green-600">${{ formatNumber(vendor.stats?.total_revenue || 0) }}</p>
                <p class="text-xs text-gray-500">Ingresos</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <p class="text-2xl font-bold text-yellow-600">⭐ {{ vendor.stats?.average_rating?.toFixed(1) || '0.0' }}</p>
                <p class="text-xs text-gray-500">Rating</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <p class="text-2xl font-bold text-blue-600">{{ vendor.stats?.total_reviews || 0 }}</p>
                <p class="text-xs text-gray-500">Reviews</p>
              </div>
            </div>
          </div>

          <!-- Compliance Flags -->
          <div v-if="vendor.compliance_flags?.length > 0" class="md:col-span-2">
            <h4 class="font-semibold text-red-700 mb-3 flex items-center gap-2">
              <span>⚠️</span> Alertas de Cumplimiento
            </h4>
            <div class="space-y-2">
              <div 
                v-for="flag in vendor.compliance_flags" 
                :key="flag"
                class="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg"
              >
                <span class="text-red-500">⚠️</span>
                <span class="text-sm text-red-700">{{ formatComplianceFlag(flag) }}</span>
              </div>
            </div>
          </div>

          <!-- Documents Status -->
          <div class="md:col-span-2">
            <h4 class="font-semibold text-gray-900 mb-3">Verificación de Documentos</h4>
            <div class="flex items-center gap-4">
              <div 
                class="flex items-center gap-2 px-4 py-2 rounded-lg"
                :class="vendor.documents_verified ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
              >
                <span>{{ vendor.documents_verified ? '✅' : '⏳' }}</span>
                <span class="text-sm font-medium">
                  {{ vendor.documents_verified ? 'Documentos Verificados' : 'Pendiente de Verificación' }}
                </span>
              </div>
              <button 
                v-if="!vendor.documents_verified"
                @click="requestDocuments(vendor)"
                class="text-sm text-blue-600 hover:underline"
              >
                Solicitar documentos →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <UiModal v-model="showRejectModal" title="Rechazar Vendor" max-width="max-w-lg">
      <p class="text-gray-600 mb-4">
        Estás rechazando a <strong>{{ selectedVendor?.business_name }}</strong>
      </p>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Razón del rechazo *</label>
          <textarea 
            v-model="rejectReason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            placeholder="Explica por qué se rechaza este vendor..."
          ></textarea>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Notas adicionales</label>
          <textarea 
            v-model="rejectNotes"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            placeholder="Notas internas..."
          ></textarea>
        </div>
      </div>
      
      <template #footer>
        <button 
          @click="showRejectModal = false"
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          Cancelar
        </button>
        <button 
          @click="rejectVendor"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          :disabled="!rejectReason"
        >
          Confirmar Rechazo
        </button>
      </template>
    </UiModal>

    <UiConfirmDialog
      v-model="showConfirm"
      :title="confirmTitle"
      :message="confirmMessage"
      :confirm-text="confirmConfirmText"
      :variant="confirmVariant"
      :loading="confirmLoading"
      @confirm="executeConfirmAction"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const pendingVendors = ref<any[]>([])
const selectedVendor = ref<any>(null)
const showRejectModal = ref(false)
const rejectReason = ref('')
const rejectNotes = ref('')

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

function openConfirm(title: string, message: string, action: () => Promise<void>, options?: { confirmText?: string, variant?: 'danger' | 'warning' | 'info' }) {
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

const loadPendingVendors = async () => {
  try {
    const response = await api.get<any[]>('/superadmin/vendors/pending')
    pendingVendors.value = response
  } catch (error) {
    console.error('Error loading pending vendors:', error)
  }
}

const confirmApproveVendor = (vendor: any) => {
  openConfirm(
    'Aprobar Vendor',
    `¿Aprobar a ${vendor.business_name}?`,
    () => executeApproveVendor(vendor)
  )
}

const executeApproveVendor = async (vendor: any) => {
  try {
    await api.post(`/superadmin/vendors/${vendor.id}/approval`, {
      action: 'approve',
      reason: 'Approved after review',
    })
    pendingVendors.value = pendingVendors.value.filter(v => v.id !== vendor.id)
    toast.success('Vendor aprobado exitosamente')
  } catch (error) {
    console.error('Error approving vendor:', error)
    toast.error('Error al aprobar vendor')
  }
}

const rejectVendor = async () => {
  if (!selectedVendor.value || !rejectReason.value) return
  
  try {
    await api.post(`/superadmin/vendors/${selectedVendor.value.id}/approval`, {
      action: 'reject',
      reason: rejectReason.value,
      notes: rejectNotes.value,
    })
    
    // Remove from list
    pendingVendors.value = pendingVendors.value.filter(v => v.id !== selectedVendor.value.id)
    showRejectModal.value = false
    rejectReason.value = ''
    rejectNotes.value = ''
    selectedVendor.value = null
    
    toast.success('Vendor rechazado')
  } catch (error) {
    console.error('Error rejecting vendor:', error)
    toast.error('Error al rechazar vendor')
  }
}

const requestDocuments = async (vendor: any) => {
  try {
    await api.post(`/superadmin/vendors/${vendor.id}/approval`, {
      action: 'request_documents',
      message: 'Por favor proporcione los documentos requeridos para completar su registro.',
    })
    toast.success('Solicitud de documentos enviada')
  } catch (error) {
    console.error('Error requesting documents:', error)
    toast.error('Error al solicitar documentos')
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatComplianceFlag = (flag: string) => {
  const flags: Record<string, string> = {
    no_properties: 'No tiene propiedades/tours registrados',
    low_completion_rate: 'Tasa de completación de reservas baja',
    low_rating: 'Rating promedio bajo',
    missing_documents: 'Documentos faltantes',
  }
  return flags[flag] || flag
}

onMounted(() => {
  loadPendingVendors()
})
</script>
