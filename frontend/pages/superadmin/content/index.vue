<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

const stats = ref({
  blogPosts: { total: 0, published: 0, drafts: 0 },
  pages: { total: 0, active: 0 },
  media: { images: 0, videos: 0, totalSize: '0 MB' },
})

const loadStats = async () => {
  try {
    const [blogData, pagesList, mediaList] = await Promise.all([
      api.get<any[]>('/superadmin/content/blog'),
      api.get<any[]>('/superadmin/content/pages'),
      api.get<any[]>('/superadmin/content/media'),
    ])
    stats.value.blogPosts.total = blogData.length
    stats.value.blogPosts.published = blogData.filter((p: any) => p.status === 'published').length
    stats.value.blogPosts.drafts = blogData.filter((p: any) => p.status === 'draft').length
    stats.value.pages.total = pagesList.length
    stats.value.pages.active = pagesList.filter((p: any) => p.is_active).length
    stats.value.media.images = mediaList.filter((m: any) => m.mime_type?.startsWith('image/')).length
    stats.value.media.videos = mediaList.filter((m: any) => m.mime_type?.startsWith('video/')).length
    const totalBytes = mediaList.reduce((sum: number, m: any) => sum + (m.size_bytes || 0), 0)
    stats.value.media.totalSize = totalBytes < 1024 * 1024
      ? `${(totalBytes / 1024).toFixed(1)} KB`
      : `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`
  } catch {
    // stats stay at defaults
  }
}

onMounted(loadStats)
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

    <!-- Blog Overview -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <NuxtLink to="/superadmin/content/blog" class="block group">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-blue-200 transition-all">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <span class="text-sm text-blue-600 font-medium group-hover:underline">Gestionar →</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-1">Blog</h3>
          <p class="text-sm text-gray-500 mb-4">Artículos, categorías y SEO</p>
          <div class="grid grid-cols-3 gap-2 text-center">
            <div class="bg-gray-50 rounded-lg p-2">
              <p class="text-lg font-bold text-gray-900">{{ stats.blogPosts.total }}</p>
              <p class="text-xs text-gray-500">Total</p>
            </div>
            <div class="bg-green-50 rounded-lg p-2">
              <p class="text-lg font-bold text-green-600">{{ stats.blogPosts.published }}</p>
              <p class="text-xs text-gray-500">Publicados</p>
            </div>
            <div class="bg-yellow-50 rounded-lg p-2">
              <p class="text-lg font-bold text-yellow-600">{{ stats.blogPosts.drafts }}</p>
              <p class="text-xs text-gray-500">Borradores</p>
            </div>
          </div>
        </div>
      </NuxtLink>

      <NuxtLink to="/superadmin/content/pages" class="block group">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-green-200 transition-all">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span class="text-sm text-green-600 font-medium group-hover:underline">Gestionar →</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-1">Páginas</h3>
          <p class="text-sm text-gray-500 mb-4">Páginas estáticas del sitio</p>
          <div class="grid grid-cols-2 gap-2 text-center">
            <div class="bg-gray-50 rounded-lg p-2">
              <p class="text-lg font-bold text-gray-900">{{ stats.pages.total }}</p>
              <p class="text-xs text-gray-500">Total</p>
            </div>
            <div class="bg-green-50 rounded-lg p-2">
              <p class="text-lg font-bold text-green-600">{{ stats.pages.active }}</p>
              <p class="text-xs text-gray-500">Activas</p>
            </div>
          </div>
        </div>
      </NuxtLink>

      <NuxtLink to="/superadmin/content/media" class="block group">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-purple-200 transition-all">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <span class="text-sm text-purple-600 font-medium group-hover:underline">Gestionar →</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-1">Media</h3>
          <p class="text-sm text-gray-500 mb-4">Biblioteca de imágenes y archivos</p>
          <div class="grid grid-cols-3 gap-2 text-center">
            <div class="bg-gray-50 rounded-lg p-2">
              <p class="text-lg font-bold text-gray-900">{{ stats.media.images }}</p>
              <p class="text-xs text-gray-500">Imágenes</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2">
              <p class="text-lg font-bold text-gray-900">{{ stats.media.videos }}</p>
              <p class="text-xs text-gray-500">Videos</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-2">
              <p class="text-lg font-bold text-gray-900">{{ stats.media.totalSize }}</p>
              <p class="text-xs text-gray-500">Espacio</p>
            </div>
          </div>
        </div>
      </NuxtLink>

      <NuxtLink to="/superadmin/content/seo" class="block group">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-amber-200 transition-all">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <span class="text-sm text-amber-600 font-medium group-hover:underline">Gestionar →</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-1">SEO Global</h3>
          <p class="text-sm text-gray-500 mb-4">Meta tags, robots.txt, sitemap</p>
          <div class="text-sm text-gray-400">
            Configuración SEO del sitio completo
          </div>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
