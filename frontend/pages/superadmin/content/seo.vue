<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const keywordInput = ref('')

const { values: form, saving, saveError, save, setField } = useForm<SEOSettingsUpdate>({
  initial: {},
  validate: () => ({}),
  onSave: async (v) => {
    const dirty: Record<string, any> = {}
    for (const [key, value] of Object.entries(v)) {
      if (value !== undefined) dirty[key] = value
    }
    await api.put('/superadmin/content/seo', dirty)
  },
})

const loaded = ref(false)

const loadSettings = async () => {
  try {
    const s = await api.get<SEOSettings>('/superadmin/content/seo')
    setField('site_title_template', s.site_title_template)
    setField('default_meta_title', s.default_meta_title)
    setField('default_meta_description', s.default_meta_description)
    setField('default_meta_keywords', s.default_meta_keywords)
    setField('google_site_verification', s.google_site_verification)
    setField('robots_txt', s.robots_txt)
    setField('sitemap_enabled', s.sitemap_enabled)
    setField('structured_data_enabled', s.structured_data_enabled)
    loaded.value = true
  } catch (error: any) {
    toast.error(error?.data?.detail || 'Error al cargar configuración SEO')
  }
}

const addKeyword = () => {
  const kw = keywordInput.value.trim().toLowerCase()
  const existing = form.value.default_meta_keywords || []
  if (kw && !existing.includes(kw)) {
    setField('default_meta_keywords', [...existing, kw])
  }
  keywordInput.value = ''
}

const removeKeyword = (index: number) => {
  const existing = form.value.default_meta_keywords || []
  existing.splice(index, 1)
  setField('default_meta_keywords', [...existing])
}

async function handleSave() {
  try {
    await save()
    toast.success('Configuración SEO guardada')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al guardar SEO')
  }
}

onMounted(loadSettings)
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Configuración SEO Global</h1>
        <p class="text-gray-500 text-sm mt-1">Gestiona el SEO de todo el sitio</p>
      </div>
    </div>

    <UiAlert v-if="saveError" variant="error" dismissible>
      {{ saveError }}
    </UiAlert>

    <div v-if="!loaded" class="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
      <UiSkeleton variant="card" />
    </div>

    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <UiInput
          :model-value="form.site_title_template || ''"
          label="Template de Título"
          placeholder="{page_title} | {site_name}"
          hint="Usa {page_title} y {site_name} como variables"
          @update:model-value="(v) => setField('site_title_template', v)"
        />
        <UiInput
          :model-value="form.default_meta_title || ''"
          label="Meta Title por Defecto"
          @update:model-value="(v) => setField('default_meta_title', v)"
        />
      </div>

      <UiTextarea
        :model-value="form.default_meta_description || ''"
        label="Meta Description por Defecto"
        :maxLength="160"
        rows="3"
        @update:model-value="(v) => setField('default_meta_description', v)"
      />

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Palabras Clave</label>
        <div class="flex flex-wrap gap-2 mb-2">
          <span
            v-for="(kw, i) in form.default_meta_keywords"
            :key="i"
            class="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-full text-sm"
          >
            {{ kw }}
            <button @click="removeKeyword(i)" class="text-primary-500 hover:text-primary-700">&times;</button>
          </span>
        </div>
        <div class="flex gap-2">
          <UiInput
            :model-value="keywordInput"
            placeholder="Escribe y presiona Enter"
            class="flex-1"
            @update:model-value="keywordInput = $event"
            @keyup.enter="addKeyword"
          />
          <button @click="addKeyword" class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
            Agregar
          </button>
        </div>
      </div>

      <UiInput
        :model-value="form.google_site_verification || ''"
        label="Google Site Verification"
        placeholder="código de verificación de Google Search Console"
        @update:model-value="(v) => setField('google_site_verification', v)"
      />

      <UiTextarea
        :model-value="form.robots_txt || ''"
        label="robots.txt"
        rows="4"
        @update:model-value="(v) => setField('robots_txt', v)"
      />

      <div class="flex flex-wrap gap-6">
        <UiCheckbox
          :model-value="!!form.sitemap_enabled"
          label="Sitemap habilitado"
          @update:model-value="(v) => setField('sitemap_enabled', v)"
        />
        <UiCheckbox
          :model-value="!!form.structured_data_enabled"
          label="Datos estructurados (JSON-LD)"
          @update:model-value="(v) => setField('structured_data_enabled', v)"
        />
      </div>

      <div class="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="handleSave"
          :disabled="saving"
          class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <UiSpinner v-if="saving" size="sm" color="white" />
          {{ saving ? 'Guardando...' : 'Guardar Configuración SEO' }}
        </button>
      </div>
    </div>
  </div>
</template>
