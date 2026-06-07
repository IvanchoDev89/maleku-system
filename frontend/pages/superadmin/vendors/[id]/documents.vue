<script setup lang="ts">
/**
 * Vendor Documents Verification Page
 * Verificación de documentos de proveedor
 */
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const vendorId = route.params.id as string
const toast = useToast()

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

const vendor = ref({
  id: vendorId,
  name: 'Transportes CR',
  email: 'contact@transportescr.com',
  status: 'pending',
  submitted_at: '2024-02-15'
})

const documents = ref([
  {
    id: 'doc-001',
    name: 'Cédula Jurídica',
    type: 'legal_id',
    filename: 'cedula_juridica.pdf',
    url: '#',
    status: 'pending',
    uploaded_at: '2024-02-15 10:30',
    notes: ''
  },
  {
    id: 'doc-002',
    name: 'Permiso de Operación',
    type: 'operating_permit',
    filename: 'permiso_operacion.pdf',
    url: '#',
    status: 'verified',
    uploaded_at: '2024-02-15 10:35',
    notes: 'Válido hasta 2025'
  },
  {
    id: 'doc-003',
    name: 'Seguro de Responsabilidad Civil',
    type: 'insurance',
    filename: 'seguro_rc.pdf',
    url: '#',
    status: 'rejected',
    uploaded_at: '2024-02-15 10:40',
    notes: 'Monto insuficiente, requiere mínimo $100,000'
  },
  {
    id: 'doc-004',
    name: 'Foto de Flota',
    type: 'fleet_photo',
    filename: 'flota_2024.jpg',
    url: '#',
    status: 'pending',
    uploaded_at: '2024-02-15 11:00',
    notes: ''
  }
])

const verificationNotes = ref('')

const verifiedCount = computed(() => documents.value.filter(d => d.status === 'verified').length)
const totalCount = computed(() => documents.value.length)
const progressPercent = computed(() => Math.round((verifiedCount.value / totalCount.value) * 100))

const verifyDocument = (docId: string) => {
  const doc = documents.value.find(d => d.id === docId)
  if (doc) doc.status = 'verified'
}

const rejectDocument = (docId: string) => {
  const doc = documents.value.find(d => d.id === docId)
  if (doc) doc.status = 'rejected'
}

const approveVendor = () => {
  vendor.value.status = 'active'
  toast.success('Proveedor aprobado exitosamente')
  router.push('/superadmin/vendors')
}

const confirmRejectVendor = () => {
  openConfirm(
    'Rechazar Proveedor',
    '¿Estás seguro de rechazar este proveedor?',
    executeRejectVendor
  )
}

const executeRejectVendor = () => {
  vendor.value.status = 'rejected'
  router.push('/superadmin/vendors')
}

const goBack = () => {
  router.push('/superadmin/vendors')
}

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  verified: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800'
}

const statusLabels = {
  pending: 'Pendiente',
  verified: 'Verificado',
  rejected: 'Rechazado'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button @click="goBack" class="p-2 hover:bg-gray-100 rounded-lg">
          <span class="text-2xl">←</span>
        </button>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Verificación de Documentos</h1>
          <p class="text-gray-500">{{ vendor.name }} - ID: {{ vendorId }}</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button 
          @click="confirmRejectVendor"
          class="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
        >
          Rechazar Proveedor
        </button>
        <button 
          @click="approveVendor"
          :disabled="verifiedCount < totalCount"
          :class="verifiedCount >= totalCount ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-300 cursor-not-allowed'"
          class="px-4 py-2 text-white rounded-lg"
        >
          ✓ Aprobar Proveedor
        </button>
      </div>
    </div>

    <!-- Progress -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">Progreso de Verificación</span>
        <span class="text-sm font-medium text-gray-900">{{ verifiedCount }} de {{ totalCount }} documentos</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          class="bg-green-600 h-2.5 rounded-full transition-all duration-300" 
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
      <div class="mt-2 text-sm" :class="progressPercent === 100 ? 'text-green-600' : 'text-yellow-600'">
        {{ progressPercent === 100 ? '✓ Todos los documentos verificados' : 'Faltan documentos por verificar' }}
      </div>
    </div>

    <!-- Documents Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div 
        v-for="doc in documents" 
        :key="doc.id"
        class="bg-white rounded-lg shadow overflow-hidden"
      >
        <!-- Document Header -->
        <div class="p-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <span class="text-xl">📄</span>
              </div>
              <div>
                <h3 class="font-medium text-gray-900">{{ doc.name }}</h3>
                <p class="text-sm text-gray-500">{{ doc.filename }}</p>
              </div>
            </div>
            <span :class="['px-3 py-1 rounded-full text-xs font-medium', statusColors[doc.status]]">
              {{ statusLabels[doc.status] }}
            </span>
          </div>
        </div>

        <!-- Document Preview Placeholder -->
        <div class="h-48 bg-gray-100 flex items-center justify-center">
          <div class="text-center">
            <span class="text-4xl mb-2">📄</span>
            <p class="text-sm text-gray-500">Vista previa del documento</p>
            <a 
              :href="doc.url" 
              target="_blank"
              class="mt-2 inline-block text-blue-600 hover:text-blue-800 text-sm"
            >
              Abrir documento →
            </a>
          </div>
        </div>

        <!-- Actions -->
        <div class="p-4 border-t border-gray-200">
          <div class="flex gap-2">
            <button 
              @click="verifyDocument(doc.id)"
              :disabled="doc.status === 'verified'"
              :class="doc.status === 'verified' ? 'bg-gray-100 text-gray-400' : 'bg-green-50 text-green-600 hover:bg-green-100'"
              class="flex-1 py-2 rounded-lg text-sm font-medium"
            >
              ✓ Verificar
            </button>
            <button 
              @click="rejectDocument(doc.id)"
              :disabled="doc.status === 'rejected'"
              :class="doc.status === 'rejected' ? 'bg-gray-100 text-gray-400' : 'bg-red-50 text-red-600 hover:bg-red-100'"
              class="flex-1 py-2 rounded-lg text-sm font-medium"
            >
              ✗ Rechazar
            </button>
          </div>
          <textarea 
            v-if="doc.status === 'rejected' || doc.notes"
            v-model="doc.notes"
            placeholder="Notas sobre este documento..."
            class="mt-3 w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            rows="2"
          ></textarea>
        </div>
      </div>
    </div>

    <!-- Verification Notes -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Notas de Verificación</h3>
      <textarea 
        v-model="verificationNotes"
        placeholder="Notas generales sobre la verificación de este proveedor..."
        class="w-full px-4 py-3 border border-gray-300 rounded-lg"
        rows="4"
      ></textarea>
      <div class="mt-4 flex justify-end gap-3">
        <button 
          @click="goBack"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button 
          @click="approveVendor"
          :disabled="verifiedCount < totalCount"
          :class="verifiedCount >= totalCount ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-gray-300 text-gray-500 cursor-not-allowed'"
          class="px-4 py-2 rounded-lg"
        >
          Aprobar Proveedor
        </button>
      </div>
    </div>

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
