<script setup lang="ts">
/**
 * Content Management - Main Page
 * Gestión de blog, páginas estáticas y media
 */
import { ref } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const activeTab = ref<'blog' | 'pages' | 'media'>('blog')

const contentStats = ref({
  blogPosts: { total: 45, published: 38, drafts: 7 },
  pages: { total: 12, active: 12 },
  media: { images: 234, videos: 12, totalSize: '1.2 GB' }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Contenido</h1>
        <p class="mt-1 text-gray-500">Blog, páginas estáticas y biblioteca de medios</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in ['blog', 'pages', 'media']"
          :key="tab"
          @click="activeTab = tab as any"
          :class="[
            activeTab === tab
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize'
          ]"
        >
          {{ tab === 'blog' ? 'Blog' : tab === 'pages' ? 'Páginas' : 'Media' }}
        </button>
      </nav>
    </div>

    <!-- Stats based on active tab -->
    <div v-if="activeTab === 'blog'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Artículos</div>
        <div class="text-3xl font-bold text-gray-900">{{ contentStats.blogPosts.total }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Publicados</div>
        <div class="text-3xl font-bold text-green-600">{{ contentStats.blogPosts.published }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Borradores</div>
        <div class="text-3xl font-bold text-yellow-600">{{ contentStats.blogPosts.drafts }}</div>
      </div>
    </div>

    <div v-else-if="activeTab === 'pages'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Páginas Totales</div>
        <div class="text-3xl font-bold text-gray-900">{{ contentStats.pages.total }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Páginas Activas</div>
        <div class="text-3xl font-bold text-green-600">{{ contentStats.pages.active }}</div>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Imágenes</div>
        <div class="text-3xl font-bold text-gray-900">{{ contentStats.media.images }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Videos</div>
        <div class="text-3xl font-bold text-gray-900">{{ contentStats.media.videos }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Espacio Usado</div>
        <div class="text-3xl font-bold text-gray-900">{{ contentStats.media.totalSize }}</div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex space-x-4">
      <button
        v-if="activeTab === 'blog'"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
      >
        + Nuevo Artículo
      </button>
      <button
        v-else-if="activeTab === 'pages'"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
      >
        + Nueva Página
      </button>
      <button
        v-else
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
      >
        + Subir Archivo
      </button>
    </div>

    <!-- Content Placeholder -->
    <div class="bg-white rounded-lg shadow p-6">
      <p class="text-gray-500">Vista de {{ activeTab }} se cargará aquí...</p>
    </div>
  </div>
</template>
