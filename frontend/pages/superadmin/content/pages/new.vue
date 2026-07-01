<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const router = useRouter()
const api = useApi()
const toast = useToast()

const slugManuallyEdited = ref(false)

const { values: form, saving, saveError, save, isDirty, submitted, setField } = useForm<StaticPageCreate>({
  initial: {
    title: '',
    slug: '',
    content: '',
    template: 'default',
    meta_title: null,
    meta_description: null,
    is_active: true,
    show_in_footer: false,
    show_in_header: false,
    sort_order: 0,
  },
  validate: (v) => {
    const errs: Record<string, string> = {}
    if (!v.title?.trim()) errs.title = 'El título es requerido'
    if (!v.slug?.trim()) errs.slug = 'El slug es requerido'
    return errs
  },
  onSave: async (v) => {
    await api.post('/superadmin/content/pages', v)
    toast.success('Página creada exitosamente')
    router.push('/superadmin/content/pages')
  },
})

function generateSlug() {
  if (slugManuallyEdited.value) return
  setField('slug', (form.value.title || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, ''))
}

function onSlugInput() {
  slugManuallyEdited.value = true
}

async function handleSave() {
  try {
    await save()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al crear página')
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Nueva Página</h1>
        <p class="text-gray-500 text-sm mt-1">Crear una nueva página estática</p>
      </div>
      <NuxtLink to="/superadmin/content/pages" class="text-primary-600 hover:text-primary-700 text-sm">
        ← Volver
      </NuxtLink>
    </div>

    <UiAlert v-if="saveError" variant="error" dismissible>
      {{ saveError }}
    </UiAlert>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <UiInput
          :model-value="form.title"
          label="Título"
          placeholder="Título de la página"
          required
          :error="submitted && !form.title?.trim() ? 'El título es requerido' : undefined"
          @update:model-value="(v) => { setField('title', v); generateSlug() }"
        />
        <UiInput
          :model-value="form.slug"
          label="Slug"
          placeholder="url-friendly-slug"
          required
          :error="submitted && !form.slug?.trim() ? 'El slug es requerido' : undefined"
          @update:model-value="(v) => { setField('slug', v); onSlugInput() }"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contenido (HTML)</label>
        <textarea
          :value="form.content"
          @input="(e: any) => setField('content', e.target.value)"
          rows="12"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          placeholder="<h1>Título</h1><p>Contenido de la página...</p>"
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Template</label>
          <select
            :value="form.template"
            @change="(e: any) => setField('template', e.target.value)"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="default">Default</option>
            <option value="full-width">Full Width</option>
            <option value="landing">Landing</option>
            <option value="contact">Contacto</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Orden</label>
          <input
            :value="form.sort_order"
            @input="(e: any) => setField('sort_order', parseInt(e.target.value) || 0)"
            type="number"
            min="0"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      <div class="flex flex-wrap gap-6">
        <UiCheckbox
          :model-value="!!form.is_active"
          label="Activa"
          @update:model-value="(v) => setField('is_active', v)"
        />
        <UiCheckbox
          :model-value="!!form.show_in_header"
          label="Mostrar en Header"
          @update:model-value="(v) => setField('show_in_header', v)"
        />
        <UiCheckbox
          :model-value="!!form.show_in_footer"
          label="Mostrar en Footer"
          @update:model-value="(v) => setField('show_in_footer', v)"
        />
      </div>

      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">SEO</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <UiInput
            :model-value="form.meta_title || ''"
            label="Meta Title"
            placeholder="Título SEO (máx. 70 caracteres)"
            @update:model-value="(v) => setField('meta_title', v || null)"
          />
          <UiTextarea
            :model-value="form.meta_description || ''"
            label="Meta Description"
            :maxLength="160"
            rows="2"
            placeholder="Descripción SEO (máx. 160 caracteres)"
            @update:model-value="(v) => setField('meta_description', v || null)"
          />
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <NuxtLink
          to="/superadmin/content/pages"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Cancelar
        </NuxtLink>
        <button
          @click="handleSave"
          :disabled="saving || !form.title || !form.slug"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <UiSpinner v-if="saving" size="sm" color="white" />
          {{ saving ? 'Guardando...' : 'Guardar Página' }}
        </button>
      </div>
    </div>
  </div>
</template>
