<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()

const pageLoaded = ref(false)

const { values: form, saving, saveError, save, setField, setOriginal, isDirty } = useForm<StaticPageUpdate>({
  initial: {},
  validate: () => ({}),
  onSave: async (v) => {
    const dirty: Record<string, any> = {}
    for (const [key, value] of Object.entries(v)) {
      if (value !== undefined) dirty[key] = value
    }
    await api.put(`/superadmin/content/pages/${route.params.id}`, dirty)
    toast.success('Página actualizada')
    router.push('/superadmin/content/pages')
  },
})

const loadPage = async () => {
  try {
    const page = await api.get<StaticPage>(`/superadmin/content/pages/${route.params.id}`)
    setOriginal({
      title: page.title,
      slug: page.slug,
      content: page.content,
      template: page.template,
      meta_title: page.meta_title,
      meta_description: page.meta_description,
      is_active: page.is_active,
      show_in_footer: page.show_in_footer,
      show_in_header: page.show_in_header,
      sort_order: page.sort_order,
    })
    pageLoaded.value = true
  } catch (error: any) {
    toast.error(error?.data?.detail || 'Error al cargar página')
    router.push('/superadmin/content/pages')
  }
}

async function handleSave() {
  try {
    await save()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al actualizar página')
  }
}

onMounted(loadPage)
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Editar Página</h1>
        <p class="text-gray-500 text-sm mt-1">Modificar página estática</p>
      </div>
      <NuxtLink to="/superadmin/content/pages" class="text-primary-600 hover:text-primary-700 text-sm">
        ← Volver
      </NuxtLink>
    </div>

    <UiAlert v-if="saveError" variant="error" dismissible>
      {{ saveError }}
    </UiAlert>

    <div v-if="!pageLoaded" class="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
      <UiSkeleton variant="card" />
    </div>

    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
      <div class="flex items-center gap-2 text-sm" v-if="isDirty">
        <span class="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
        <span class="text-amber-600 font-medium">Cambios sin guardar</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <UiInput
          :model-value="form.title || ''"
          label="Título"
          @update:model-value="(v) => setField('title', v)"
        />
        <UiInput
          :model-value="form.slug || ''"
          label="Slug"
          @update:model-value="(v) => setField('slug', v)"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contenido (HTML)</label>
        <textarea
          :value="form.content"
          @input="(e: any) => setField('content', e.target.value)"
          rows="12"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
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
            @update:model-value="(v) => setField('meta_title', v || null)"
          />
          <UiTextarea
            :model-value="form.meta_description || ''"
            label="Meta Description"
            :maxLength="160"
            rows="2"
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
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <UiSpinner v-if="saving" size="sm" color="white" />
          {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>
