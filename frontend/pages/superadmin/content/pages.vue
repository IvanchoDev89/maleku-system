<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

interface Page {
  id: string
  title: string
  slug: string
  template: string
  is_active: boolean
  show_in_footer: boolean
  show_in_header: boolean
  sort_order: number
  updated_at: string
}

const pages = ref<Page[]>([])
const loading = ref(true)

const fetchPages = async () => {
  loading.value = true
  try {
    const response = await api.get('/superadmin/content/pages')
    pages.value = response.items || response || []
  } catch (error) {
    console.error('Error fetching pages:', error)
    pages.value = []
  } finally {
    loading.value = false
  }
}

const toggleActive = async (page: Page) => {
  try {
    await api.put(`/superadmin/content/pages/${page.id}`, { is_active: !page.is_active })
    page.is_active = !page.is_active
  } catch (error) {
    console.error('Error toggling page:', error)
  }
}

onMounted(() => {
  fetchPages()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">Paginas Estaticas</h1>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500">Cargando paginas...</p>
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pagina</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Template</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Header</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Footer</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Active</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="page in pages" :key="page.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="font-medium text-gray-900">{{ page.title }}</div>
                <div class="text-sm text-gray-500">/{{ page.slug }}</div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 hidden sm:table-cell">{{ page.template }}</td>
              <td class="px-6 py-4 text-center">
                <span :class="page.show_in_header ? 'text-green-600' : 'text-gray-300'">
                  {{ page.show_in_header ? '✓' : '—' }}
                </span>
              </td>
              <td class="px-6 py-4 text-center">
                <span :class="page.show_in_footer ? 'text-green-600' : 'text-gray-300'">
                  {{ page.show_in_footer ? '✓' : '—' }}
                </span>
              </td>
              <td class="px-6 py-4 text-center">
                <button @click="toggleActive(page)" :class="page.is_active ? 'text-green-600' : 'text-gray-300'">
                  {{ page.is_active ? '●' : '○' }}
                </button>
              </td>
              <td class="px-6 py-4 text-right space-x-2">
                <button class="text-primary-600 hover:text-primary-900 text-sm">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
