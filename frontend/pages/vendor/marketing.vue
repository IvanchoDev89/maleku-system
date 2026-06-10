<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Marketing</h1>
        <p class="text-gray-600">Conecta con tus clientes y aumenta tus reservas</p>
      </div>
      <button
        @click="showCampaignModal = true"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
      >
        <Icon name="lucide:send" class="w-4 h-4 inline mr-2" />
        Nueva Promoción
      </button>
    </div>

    <!-- Stats -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Campañas</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_campaigns }}</p>
          </div>
          <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:megaphone" class="w-6 h-6 text-primary-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Clientes Alcanzados</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(stats.total_recipients) }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:users" class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Aperturas</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(stats.total_opens) }}</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:eye" class="w-6 h-6 text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Engagement Rate</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.engagement_rate }}%</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:trending-up" class="w-6 h-6 text-purple-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Campaigns -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-lg font-semibold text-gray-900">Tus Promociones</h2>
      </div>

      <div v-if="loading" class="p-12 text-center">
        <Icon name="lucide:loader" class="w-8 h-8 animate-spin text-primary-600 mx-auto" />
        <p class="mt-4 text-gray-600">Cargando...</p>
      </div>

      <div v-else-if="campaigns.length === 0" class="p-12 text-center">
        <Icon name="lucide:megaphone" class="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p class="text-gray-600">Aún no has creado promociones</p>
        <button
          @click="showCampaignModal = true"
          class="mt-4 text-primary-600 hover:underline"
        >
          Crear tu primera promoción
        </button>
      </div>

      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="campaign in campaigns"
          :key="campaign.id"
          class="p-6 hover:bg-gray-50 transition"
        >
          <div class="flex items-start justify-between">
            <div>
              <h3 class="font-semibold text-gray-900">{{ campaign.name }}</h3>
              <p class="text-sm text-gray-500 mt-1">{{ campaign.subject }}</p>
              <div class="flex items-center gap-4 mt-3">
                <span :class="statusClass(campaign.status)">
                  {{ statusLabel(campaign.status) }}
                </span>
                <span class="text-sm text-gray-500">
                  <Icon name="lucide:users" class="w-4 h-4 inline mr-1" />
                  {{ formatNumber(campaign.total_recipients) }} destinatarios
                </span>
                <span class="text-sm text-gray-500">
                  <Icon name="lucide:eye" class="w-4 h-4 inline mr-1" />
                  {{ campaign.open_rate }}% apertura
                </span>
                <span class="text-sm text-gray-500">
                  <Icon name="lucide:pointer" class="w-4 h-4 inline mr-1" />
                  {{ campaign.click_rate }}% clics
                </span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-500">{{ formatDate(campaign.created_at) }}</p>
              <button
                v-if="campaign.status === 'draft'"
                @click="sendCampaign(campaign.id)"
                :disabled="sendingId === campaign.id"
                class="mt-2 px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                <Icon v-if="sendingId === campaign.id" name="lucide:loader" class="w-4 h-4 animate-spin inline mr-1" />
                <Icon v-else name="lucide:send" class="w-4 h-4 inline mr-1" />
                Enviar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tips -->
    <div class="mt-8 bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-6">
      <h3 class="font-semibold text-gray-900 mb-3">
        <Icon name="lucide:lightbulb" class="w-5 h-5 inline mr-2" />
        Consejos para mejores resultados
      </h3>
      <ul class="space-y-2 text-sm text-gray-700">
        <li>• Envía promociones los martes o miércoles para mayor apertura</li>
        <li>• Usa asuntos cortos y atractivos (menos de 50 caracteres)</li>
        <li>• Incluye imágenes de tus propiedades o tours</li>
        <li>• Segmenta por intereses de tus clientes anteriores</li>
      </ul>
    </div>

    <!-- Create Campaign Modal (simplified) -->
    <UiModal v-model="showCampaignModal" title="Nueva Promoción" max-width="max-w-2xl">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de la promoción</label>
          <input
            v-model="newCampaign.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg"
            placeholder="Ej: Descuento de Verano 2024"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Asunto del email</label>
          <input
            v-model="newCampaign.subject"
            type="text"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg"
            placeholder="Ej: ¡50% de descuento en tours de aventura!"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Contenido HTML</label>
          <textarea
            v-model="newCampaign.html_content"
            rows="6"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg"
            placeholder="<h1>¡Oferta especial!</h1><p>...</p>"
          ></textarea>
        </div>
      </div>
      <template #footer>
        <button
          @click="showCampaignModal = false"
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          Cancelar
        </button>
        <button
          @click="createCampaign"
          :disabled="!isValidCampaign || creating"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
        >
          <Icon v-if="creating" name="lucide:loader" class="w-4 h-4 animate-spin inline mr-1" />
          Crear Promoción
        </button>
      </template>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const { $toast } = useNuxtApp() as unknown as { $toast: any }
const marketing = useMarketing()

// State
const showCampaignModal = ref(false)
const sendingId = ref<string | null>(null)
const creating = ref(false)

const newCampaign = ref({
  name: '',
  subject: '',
  html_content: '',
  campaign_type: 'promotion',
  recipient_type: 'vendor_customers'
})

// Data
const campaigns = computed(() => marketing.campaigns.value)
const stats = computed(() => marketing.vendorStats.value)
const loading = computed(() => marketing.loading.value)

const isValidCampaign = computed(() => {
  return newCampaign.value.name &&
    newCampaign.value.subject &&
    newCampaign.value.html_content.length > 10
})

// Load data
onMounted(async () => {
  try {
    await Promise.all([
      marketing.listVendorCampaigns(),
      marketing.getVendorAnalytics()
    ])
  } catch (err: any) {
    $toast.error('Error cargando datos')
  }
})

// Methods
const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    draft: 'px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
    scheduled: 'px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
    sending: 'px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800',
    sent: 'px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800'
  }
  return classes[status] || classes.draft
}

const statusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: 'Borrador',
    scheduled: 'Programado',
    sending: 'Enviando',
    sent: 'Enviado'
  }
  return labels[status] || status
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('es-CR').format(num || 0)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const createCampaign = async () => {
  creating.value = true
  try {
    await marketing.createVendorCampaign(newCampaign.value)
    $toast.success('Promoción creada exitosamente')
    showCampaignModal.value = false
    await marketing.listVendorCampaigns()
    // Reset form
    newCampaign.value = {
      name: '',
      subject: '',
      html_content: '',
      campaign_type: 'promotion',
      recipient_type: 'vendor_customers'
    }
  } catch (err: any) {
    $toast.error(err.message || 'Error creando promoción')
  } finally {
    creating.value = false
  }
}

const sendCampaign = async (id: string) => {
  sendingId.value = id
  try {
    await marketing.sendCampaign(id)
    $toast.success('Promoción enviada exitosamente')
    await marketing.listVendorCampaigns()
  } catch (err: any) {
    $toast.error(err.message || 'Error enviando promoción')
  } finally {
    sendingId.value = null
  }
}
</script>
