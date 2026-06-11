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
      <div v-if="activeCategory === 'general'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">⚙️ Configuración General</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Nombre del Sitio</label>
            <input v-model="settings.site_name" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Descripción</label>
            <input v-model="settings.site_description" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Palabras Clave SEO</label>
            <input v-model="settings.site_keywords" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Logo URL</label>
            <input v-model="settings.site_logo" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
        </div>
      </div>

      <div v-if="activeCategory === 'contact'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">📞 Información de Contacto</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Email de Contacto</label>
            <input v-model="settings.contact_email" type="email" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Teléfono</label>
            <input v-model="settings.contact_phone" type="tel" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">WhatsApp</label>
            <input v-model="settings.contact_whatsapp" type="tel" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Dirección</label>
            <input v-model="settings.contact_address" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
        </div>
      </div>

      <div v-if="activeCategory === 'business'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">💰 Configuración de Negocios</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Tasa de Comisión (%)</label>
            <input v-model.number="settings.commission_rate" type="number" min="0" max="100" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Moneda</label>
            <UiSelect v-model="settings.currency" :options="currencyOptions" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Monto Mínimo de Reserva</label>
            <input v-model.number="settings.min_booking_amount" type="number" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Horas para Cancelar</label>
            <input v-model.number="settings.booking_cancellation_hours" type="number" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
        </div>
      </div>

      <div v-if="activeCategory === 'social'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">📱 Redes Sociales</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Facebook</label>
            <input v-model="settings.social_facebook" type="url" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Instagram</label>
            <input v-model="settings.social_instagram" type="url" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Twitter/X</label>
            <input v-model="settings.social_twitter" type="url" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">YouTube</label>
            <input v-model="settings.social_youtube" type="url" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
        </div>
      </div>

      <div v-if="activeCategory === 'seo'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">🔍 Configuración SEO</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Imagen OG por Defecto</label>
            <input v-model="settings.seo_og_image" type="url" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Google Analytics ID</label>
            <input v-model="settings.seo_google_analytics_id" type="text" placeholder="G-XXXXXXXXXX" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Google Search Console</label>
            <input v-model="settings.seo_google_search_console" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Directivas Robots</label>
            <input v-model="settings.seo_robots" type="text" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
          </div>
        </div>
      </div>

      <div v-if="activeCategory === 'appearance'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">🎨 Apariencia</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Color Primario</label>
            <div class="flex gap-3">
              <input v-model="settings.theme_primary_color" type="color" class="w-14 h-11 rounded-xl cursor-pointer border border-gray-200" />
              <input v-model="settings.theme_primary_color" type="text" class="flex-1 bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
            </div>
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Color Secundario</label>
            <div class="flex gap-3">
              <input v-model="settings.theme_secondary_color" type="color" class="w-14 h-11 rounded-xl cursor-pointer border border-gray-200" />
              <input v-model="settings.theme_secondary_color" type="text" class="flex-1 bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
            </div>
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Color de Acento</label>
            <div class="flex gap-3">
              <input v-model="settings.theme_accent_color" type="color" class="w-14 h-11 rounded-xl cursor-pointer border border-gray-200" />
              <input v-model="settings.theme_accent_color" type="text" class="flex-1 bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
            </div>
          </div>
          <div>
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Fuente</label>
            <UiSelect v-model="settings.theme_font_family" :options="fontOptions" />
          </div>
        </div>
      </div>

      <div v-if="activeCategory === 'maintenance'" class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-gray-900 font-bold text-lg mb-5">🔧 Mantenimiento</h3>
        <div class="space-y-4">
          <label class="flex items-center gap-3 cursor-pointer p-3 rounded-xl hover:bg-gray-50 transition-colors">
            <input v-model="settings.maintenance_mode" type="checkbox" class="w-5 h-5 text-primary rounded focus:ring-primary" />
            <div>
              <span class="text-gray-700 font-medium">Modo Mantenimiento</span>
              <p class="text-gray-400 text-sm">Muestra página de mantenimiento a visitantes</p>
            </div>
          </label>
          <div v-if="settings.maintenance_mode" class="pl-8">
            <label class="block text-gray-500 text-sm mb-1.5 font-medium">Mensaje de Mantenimiento</label>
            <textarea v-model="settings.maintenance_message" rows="3" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20"></textarea>
          </div>
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

const categories = [
  { key: 'general', label: 'General', icon: '⚙️' },
  { key: 'contact', label: 'Contacto', icon: '📞' },
  { key: 'business', label: 'Negocio', icon: '💰' },
  { key: 'social', label: 'Social', icon: '📱' },
  { key: 'seo', label: 'SEO', icon: '🔍' },
  { key: 'appearance', label: 'Apariencia', icon: '🎨' },
  { key: 'maintenance', label: 'Mantenimiento', icon: '🔧' }
]

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