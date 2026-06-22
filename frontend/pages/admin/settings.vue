<template>
  <div>
    <div class="flex gap-2 mb-6 overflow-x-auto pb-2">
      <button
        v-for="cat in categories"
        :key="cat.key"
        @click="activeCategory = cat.key"
        class="px-5 py-2.5 rounded-xl font-medium whitespace-nowrap transition-all shadow-sm"
        :class="activeCategory === cat.key ? 'bg-primary text-white shadow-md' : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 border border-gray-200'"
      >
        {{ cat.icon }} {{ cat.label }}
      </button>
    </div>

    <div class="space-y-6">
      <div v-for="section in sections" :key="section.key" v-if="activeCategory === section.key" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">{{ section.icon }} {{ section.title }}</h3>
        <div :class="section.noGrid ? 'space-y-4' : 'grid grid-cols-1 md:grid-cols-2 gap-5'">
          <template v-for="field in section.fields" :key="field.key">
            <div v-if="field.type === 'text' || field.type === 'email' || field.type === 'tel' || field.type === 'url'" :class="field.fullWidth ? 'md:col-span-2' : ''">
              <label class="block text-gray-500 text-sm mb-1.5 font-medium">{{ field.label }}</label>
              <input :type="field.type" v-model="settings[field.key]" :placeholder="field.placeholder || ''" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
            </div>
            <div v-else-if="field.type === 'number'" :class="field.fullWidth ? 'md:col-span-2' : ''">
              <label class="block text-gray-500 text-sm mb-1.5 font-medium">{{ field.label }}</label>
              <input :type="field.type" v-model.number="settings[field.key]" :min="field.min" :max="field.max" :step="field.step" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
            </div>
            <div v-else-if="field.type === 'select'" :class="field.fullWidth ? 'md:col-span-2' : ''">
              <label class="block text-gray-500 text-sm mb-1.5 font-medium">{{ field.label }}</label>
              <UiSelect v-model="settings[field.key]" :options="field.options" />
            </div>
            <div v-else-if="field.type === 'color'" :class="field.fullWidth ? 'md:col-span-2' : ''">
              <label class="block text-gray-500 text-sm mb-1.5 font-medium">{{ field.label }}</label>
              <div class="flex gap-3">
                <input v-model="settings[field.key]" type="color" class="w-14 h-11 rounded-xl cursor-pointer border border-gray-200" />
                <input v-model="settings[field.key]" type="text" class="flex-1 bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
              </div>
            </div>
            <div v-else-if="field.type === 'checkbox'" class="md:col-span-2">
              <label class="flex items-center gap-3 cursor-pointer p-3 rounded-xl hover:bg-gray-50 transition-colors">
                <input v-model="settings[field.key]" type="checkbox" class="w-5 h-5 text-primary rounded focus:ring-primary" />
                <div>
                  <span class="text-gray-700 font-medium">{{ field.label }}</span>
                  <p v-if="field.description" class="text-gray-400 text-sm">{{ field.description }}</p>
                </div>
              </label>
            </div>
            <div v-else-if="field.type === 'textarea' && (!field.showIf || settings[field.showIf])" class="md:col-span-2">
              <label class="block text-gray-500 text-sm mb-1.5 font-medium">{{ field.label }}</label>
              <textarea v-model="settings[field.key]" rows="3" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20"></textarea>
            </div>
          </template>
        </div>
      </div>

      <div class="flex justify-end">
        <button
          @click="saveSettings"
          class="bg-primary hover:bg-primary-700 text-white px-6 py-3 rounded-xl font-bold shadow-md hover:shadow-lg transition-all"
          :disabled="saving"
        >
          {{ saving ? '💾 Guardando...' : '💾 Guardar Cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

const api = useApi()
const auth = useAuthStore()
const toast = useToast()

const currencyOptions = [
  { value: 'USD', label: 'USD - Dólar' },
  { value: 'EUR', label: 'EUR - Euro' },
  { value: 'CRC', label: 'CRC - Colón Costarricense' },
]

const fontOptions = [
  { value: 'Outfit', label: 'Outfit' },
  { value: 'Inter', label: 'Inter' },
  { value: 'Poppins', label: 'Poppins' },
  { value: 'Roboto', label: 'Roboto' },
]

const activeCategory = ref('general')
const saving = ref(false)

const sections = [
  {
    key: 'general', icon: '⚙️', title: 'Configuración General',
    fields: [
      { key: 'site_name', label: 'Nombre del Sitio', type: 'text' },
      { key: 'site_description', label: 'Descripción', type: 'text' },
      { key: 'site_keywords', label: 'Palabras Clave SEO', type: 'text' },
      { key: 'site_logo', label: 'Logo URL', type: 'text' },
    ]
  },
  {
    key: 'contact', icon: '📞', title: 'Información de Contacto',
    fields: [
      { key: 'contact_email', label: 'Email de Contacto', type: 'email' },
      { key: 'contact_phone', label: 'Teléfono', type: 'tel' },
      { key: 'contact_whatsapp', label: 'WhatsApp', type: 'tel' },
      { key: 'contact_address', label: 'Dirección', type: 'text' },
    ]
  },
  {
    key: 'business', icon: '💰', title: 'Configuración de Negocios',
    fields: [
      { key: 'commission_rate', label: 'Tasa de Comisión (%)', type: 'number', min: 0, max: 100 },
      { key: 'currency', label: 'Moneda', type: 'select', options: currencyOptions },
      { key: 'min_booking_amount', label: 'Monto Mínimo de Reserva', type: 'number' },
      { key: 'booking_cancellation_hours', label: 'Horas para Cancelar', type: 'number' },
    ]
  },
  {
    key: 'social', icon: '📱', title: 'Redes Sociales',
    fields: [
      { key: 'social_facebook', label: 'Facebook', type: 'url' },
      { key: 'social_instagram', label: 'Instagram', type: 'url' },
      { key: 'social_twitter', label: 'Twitter/X', type: 'url' },
      { key: 'social_youtube', label: 'YouTube', type: 'url' },
    ]
  },
  {
    key: 'seo', icon: '🔍', title: 'Configuración SEO',
    fields: [
      { key: 'seo_og_image', label: 'Imagen OG por Defecto', type: 'url' },
      { key: 'seo_google_analytics_id', label: 'Google Analytics ID', type: 'text', placeholder: 'G-XXXXXXXXXX' },
      { key: 'seo_google_search_console', label: 'Google Search Console', type: 'text' },
      { key: 'seo_robots', label: 'Directivas Robots', type: 'text' },
    ]
  },
  {
    key: 'appearance', icon: '🎨', title: 'Apariencia',
    fields: [
      { key: 'theme_primary_color', label: 'Color Primario', type: 'color' },
      { key: 'theme_secondary_color', label: 'Color Secundario', type: 'color' },
      { key: 'theme_accent_color', label: 'Color de Acento', type: 'color' },
      { key: 'theme_font_family', label: 'Fuente', type: 'select', options: fontOptions },
    ]
  },
  {
    key: 'maintenance', icon: '🔧', title: 'Mantenimiento', noGrid: true,
    fields: [
      { key: 'maintenance_mode', label: 'Modo Mantenimiento', type: 'checkbox', description: 'Muestra página de mantenimiento a visitantes' },
      { key: 'maintenance_message', label: 'Mensaje de Mantenimiento', type: 'textarea', showIf: 'maintenance_mode' },
    ]
  }
]

const categories = sections.map(s => ({ key: s.key, label: s.title, icon: s.icon }))

const settings = reactive({
  site_name: 'Costa Rica Travel',
  site_description: '',
  site_keywords: '',
  site_logo: '/logo.svg',
  contact_email: '',
  contact_phone: '',
  contact_whatsapp: '',
  contact_address: '',
  commission_rate: 10,
  currency: 'USD',
  min_booking_amount: 10,
  booking_cancellation_hours: 24,
  social_facebook: '',
  social_instagram: '',
  social_twitter: '',
  social_youtube: '',
  seo_og_image: '',
  seo_google_analytics_id: '',
  seo_google_search_console: '',
  seo_robots: 'index, follow',
  theme_primary_color: '#1e7a67',
  theme_secondary_color: '#2a9d8f',
  theme_accent_color: '#e76f51',
  theme_font_family: 'Outfit',
  maintenance_mode: false,
  maintenance_message: 'Sitio en mantenimiento. Volvemos pronto.'
})

const loadSettings = async () => {
  try {
    const data = await api.get('/admin/settings')
    Object.assign(settings, data)
  } catch (error) {
    console.error('Error loading settings:', error)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await api.post('/admin/settings/bulk', settings)
    toast.success('Configuración guardada')
  } catch (error) {
    toast.error('Error al guardar')
  }
  saving.value = false
}

onMounted(() => {
  auth.initAuth()
  loadSettings()
})
</script>
