<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Marketing Dashboard</h1>
        <p class="text-gray-600">Gestión de campañas de email y analytics</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="showTemplateModal = true"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
        >
          <Icon name="lucide:file-text" class="w-4 h-4 inline mr-2" />
          Nuevo Template
        </button>
        <button
          @click="showCampaignModal = true"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
        >
          <Icon name="lucide:send" class="w-4 h-4 inline mr-2" />
          Nueva Campaña
        </button>
      </div>
    </div>

    <!-- Stats Overview -->
    <div v-if="overview" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <UiCard padding="md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Campañas</p>
            <p class="text-2xl font-bold text-gray-900">{{ overview.campaigns.total }}</p>
          </div>
          <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:mail" class="w-6 h-6 text-primary-600" />
          </div>
        </div>
        <div class="mt-4 flex items-center text-sm">
          <span class="text-green-600 font-medium">{{ overview.campaigns.sent }}</span>
          <span class="text-gray-500 ml-1">enviadas</span>
          <span class="text-gray-400 mx-2">•</span>
          <span class="text-orange-600 font-medium">{{ overview.campaigns.draft }}</span>
          <span class="text-gray-500 ml-1">borradores</span>
        </div>
      </UiCard>

      <UiCard padding="md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Enviados</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatNumber(overview.engagement.total_sent) }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:users" class="w-6 h-6 text-blue-600" />
          </div>
        </div>
        <div class="mt-4 text-sm text-gray-500">
          Destinatarios alcanzados
        </div>
      </UiCard>

      <UiCard padding="md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Tasa de Apertura</p>
            <p class="text-2xl font-bold text-gray-900">{{ overview.engagement.avg_open_rate }}%</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:eye" class="w-6 h-6 text-green-600" />
          </div>
        </div>
        <div class="mt-4 text-sm text-gray-500">
          {{ formatNumber(overview.engagement.total_opens) }} aperturas totales
        </div>
      </UiCard>

      <UiCard padding="md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Tasa de Clics</p>
            <p class="text-2xl font-bold text-gray-900">{{ overview.engagement.avg_click_rate }}%</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
            <Icon name="lucide:pointer" class="w-6 h-6 text-purple-600" />
          </div>
        </div>
        <div class="mt-4 text-sm text-gray-500">
          {{ formatNumber(overview.engagement.total_clicks) }} clics totales
        </div>
      </UiCard>
    </div>

    <!-- Campaigns List -->
    <UiCard padding="none" class="overflow-hidden">
      <div class="p-6 border-b border-gray-100">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">Campañas</h2>
          <div class="flex gap-2">
            <UiSelect v-model="statusFilter" :options="statusFilterOptions" placeholder="Todos los estados" />
            <UiSelect v-model="typeFilter" :options="typeFilterOptions" placeholder="Todos los tipos" />
          </div>
        </div>
      </div>

      <div v-if="loading" class="p-12 text-center">
        <UiSpinner size="lg" color="primary" class="mx-auto" />
        <p class="mt-4 text-gray-600">Cargando campañas...</p>
      </div>

      <div v-else-if="campaigns.length === 0" class="p-12 text-center">
        <Icon name="lucide:inbox" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p class="text-gray-600">No hay campañas aún</p>
        <button
          @click="showCampaignModal = true"
          class="mt-4 text-primary-600 hover:underline"
        >
          Crear primera campaña
        </button>
      </div>

      <table v-else class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Campaña</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Destinatarios</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Engagement</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="campaign in campaigns" :key="campaign.id" class="hover:bg-gray-50">
            <td class="px-6 py-4">
              <div>
                <p class="font-medium text-gray-900">{{ campaign.name }}</p>
                <p class="text-sm text-gray-500">{{ campaign.subject }}</p>
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass(campaign.status)">
                {{ statusLabel(campaign.status) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <p class="text-sm text-gray-900">{{ formatNumber(campaign.total_recipients) }}</p>
              <p class="text-xs text-gray-500">{{ formatNumber(campaign.sent_count) }} enviados</p>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-4">
                <div class="flex items-center gap-1">
                  <Icon name="lucide:eye" class="w-4 h-4 text-gray-400" />
                  <span class="text-sm">{{ campaign.open_rate }}%</span>
                </div>
                <div class="flex items-center gap-1">
                  <Icon name="lucide:pointer" class="w-4 h-4 text-gray-400" />
                  <span class="text-sm">{{ campaign.click_rate }}%</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <p class="text-sm text-gray-900">{{ formatDate(campaign.created_at) }}</p>
              <p v-if="campaign.sent_at" class="text-xs text-gray-500">
                Enviado: {{ formatDate(campaign.sent_at) }}
              </p>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex items-center justify-end gap-2">
                <button
                  v-if="campaign.status === 'draft'"
                  @click="sendCampaign(campaign.id)"
                  :disabled="sendingId === campaign.id"
                  class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                  title="Enviar"
                >
                  <UiSpinner v-if="sendingId === campaign.id" size="sm" color="primary" />
                  <Icon v-else name="lucide:send" class="w-4 h-4" />
                </button>
                <button
                  @click="viewAnalytics(campaign.id)"
                  class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                  title="Analytics"
                >
                  <Icon name="lucide:bar-chart-2" class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </UiCard>

    <!-- Analytics Modal -->
    <UiModal
      v-if="selectedAnalytics"
      v-model="showAnalyticsModal"
      :title="'Analytics: ' + selectedAnalytics.campaign_name"
      max-width="max-w-2xl"
    >
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-gray-50 rounded-lg p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ formatNumber(selectedAnalytics.total_recipients) }}</p>
          <p class="text-sm text-gray-600">Destinatarios</p>
        </div>
        <div class="bg-gray-50 rounded-lg p-4 text-center">
          <p class="text-2xl font-bold text-green-600">{{ selectedAnalytics.open_rate }}%</p>
          <p class="text-sm text-gray-600">Tasa Apertura</p>
        </div>
        <div class="bg-gray-50 rounded-lg p-4 text-center">
          <p class="text-2xl font-bold text-blue-600">{{ selectedAnalytics.click_rate }}%</p>
          <p class="text-sm text-gray-600">Tasa Clics</p>
        </div>
      </div>
      <div class="space-y-3">
        <div class="flex justify-between py-2 border-b border-gray-100">
          <span class="text-gray-600">Enviados</span>
          <span class="font-medium">{{ formatNumber(selectedAnalytics.sent) }}</span>
        </div>
        <div class="flex justify-between py-2 border-b border-gray-100">
          <span class="text-gray-600">Entregados</span>
          <span class="font-medium">{{ formatNumber(selectedAnalytics.delivered) }}</span>
        </div>
        <div class="flex justify-between py-2 border-b border-gray-100">
          <span class="text-gray-600">Aperturas</span>
          <span class="font-medium">{{ formatNumber(selectedAnalytics.opened) }}</span>
        </div>
        <div class="flex justify-between py-2 border-b border-gray-100">
          <span class="text-gray-600">Clics</span>
          <span class="font-medium">{{ formatNumber(selectedAnalytics.clicked) }}</span>
        </div>
        <div class="flex justify-between py-2 border-b border-gray-100">
          <span class="text-gray-600">Rebotes</span>
          <span class="font-medium">{{ formatNumber(selectedAnalytics.bounced) }}</span>
        </div>
      </div>
    </UiModal>

    <!-- Create Campaign Modal (placeholder) -->
    <UiModal v-model="showCampaignModal" title="Nueva Campaña" max-width="max-w-3xl">
      <p class="text-gray-600">Modal de creación de campaña - implementar con formulario completo</p>
      <template #footer>
        <button
          @click="showCampaignModal = false"
          class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
        >
          Cancelar
        </button>
      </template>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth', 'superadmin']
})

const { $toast } = useNuxtApp()
const marketing = useMarketing()

const statusFilterOptions = [
  { value: 'draft', label: 'Borrador' },
  { value: 'scheduled', label: 'Programado' },
  { value: 'sending', label: 'Enviando' },
  { value: 'sent', label: 'Enviado' },
]

const typeFilterOptions = [
  { value: 'newsletter', label: 'Newsletter' },
  { value: 'promotion', label: 'Promoción' },
  { value: 'welcome', label: 'Bienvenida' },
]

// State
const statusFilter = ref('')
const typeFilter = ref('')
const sendingId = ref<string | null>(null)
const showAnalyticsModal = ref(false)
const showCampaignModal = ref(false)
const showTemplateModal = ref(false)
const selectedAnalytics = ref<CampaignAnalytics | null>(null)

// Data
const campaigns = computed(() => marketing.campaigns.value)
const overview = computed(() => marketing.overview.value)
const loading = computed(() => marketing.loading.value)

// Load data
onMounted(async () => {
  try {
    await Promise.all([
      marketing.getMarketingOverview(),
      marketing.listAllCampaigns()
    ])
  } catch (err: any) {
    $toast.error('Error cargando datos de marketing')
  }
})

const sendCampaign = async (id: string) => {
  sendingId.value = id
  try {
    await marketing.sendCampaign(id)
    $toast.success('Campaña enviada exitosamente')
    await marketing.listAllCampaigns()
  } catch (err: any) {
    $toast.error(err.message || 'Error enviando campaña')
  } finally {
    sendingId.value = null
  }
}

const viewAnalytics = async (id: string) => {
  try {
    const data = await marketing.getCampaignAnalytics(id)
    selectedAnalytics.value = data
    showAnalyticsModal.value = true
  } catch (err: any) {
    $toast.error('Error cargando analytics')
  }
}
</script>
