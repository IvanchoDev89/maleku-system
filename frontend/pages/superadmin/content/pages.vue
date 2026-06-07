<script setup lang="ts">
/**
 * Static Pages Management
 * Gestión de páginas estáticas
 */
import { ref } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

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

const pages = ref<Page[]>([
  {
    id: 'page-about',
    title: 'About Us',
    slug: 'about',
    template: 'default',
    is_active: true,
    show_in_footer: true,
    show_in_header: false,
    sort_order: 1,
    updated_at: '2024-01-01'
  },
  {
    id: 'page-contact',
    title: 'Contact Us',
    slug: 'contact',
    template: 'contact',
    is_active: true,
    show_in_footer: true,
    show_in_header: true,
    sort_order: 2,
    updated_at: '2024-01-01'
  },
  {
    id: 'page-terms',
    title: 'Terms of Service',
    slug: 'terms',
    template: 'default',
    is_active: true,
    show_in_footer: true,
    show_in_header: false,
    sort_order: 3,
    updated_at: '2024-01-01'
  }
])

const toggleActive = (page: Page) => {
  page.is_active = !page.is_active
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">Static Pages</h1>
      <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
        + New Page
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Page</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Template</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Header</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Footer</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Active</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="page in pages" :key="page.id">
            <td class="px-6 py-4">
              <div class="font-medium text-gray-900">{{ page.title }}</div>
              <div class="text-sm text-gray-500">/{{ page.slug }}</div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ page.template }}</td>
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
              <button class="text-blue-600 hover:text-blue-900 text-sm">Edit</button>
              <button class="text-gray-600 hover:text-gray-900 text-sm">View</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
