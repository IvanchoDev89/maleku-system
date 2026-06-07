<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Header -->
      <div class="text-center mb-12">
        <span class="text-primary font-semibold">{{ $t('blog.title') }}</span>
        <h1 class="text-4xl font-bold mt-2">{{ $t('blog.featured') }}</h1>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Cargando artículos...</p>
      </div>

      <template v-else>
        <!-- Featured Post -->
        <div v-if="featuredPost" class="mb-12">
          <NuxtLink :to="`/blog/${featuredPost.slug}`" class="group">
            <div class="relative rounded-2xl overflow-hidden shadow-lg">
              <div class="aspect-video bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center">
                <span class="text-8xl">📝</span>
              </div>
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
              <div class="absolute bottom-0 left-0 right-0 p-8 text-white">
                <span class="px-3 py-1 bg-primary rounded-full text-sm">{{ featuredPost.category }}</span>
                <h2 class="text-3xl font-bold mt-4 group-hover:text-primary-light transition-colors">{{ featuredPost.title }}</h2>
                <p class="mt-2 opacity-90">{{ featuredPost.excerpt }}</p>
                <div class="mt-4 flex items-center gap-4 text-sm">
                  <span>👁️ {{ featuredPost.views_count }} vistas</span>
                  <span>📅 {{ formatDate(featuredPost.published_at) }}</span>
                </div>
              </div>
            </div>
          </NuxtLink>
        </div>

        <!-- Posts Grid -->
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <article 
            v-for="post in filteredPosts" 
            :key="post.id"
          class="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
        >
          <NuxtLink :to="`/blog/${post.slug}`">
            <div class="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
              <span class="text-5xl">📄</span>
            </div>
            <div class="p-6">
              <span class="text-xs font-semibold text-primary">{{ post.category }}</span>
              <h3 class="text-lg font-bold mt-2 line-clamp-2 group-hover:text-primary transition-colors">
                {{ post.title }}
              </h3>
              <p class="mt-2 text-gray-600 text-sm line-clamp-3">{{ post.excerpt }}</p>
              <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>👁️ {{ post.views_count }}</span>
                <span>{{ formatDate(post.published_at) }}</span>
              </div>
            </div>
          </NuxtLink>
        </article>
      </div>

        <!-- Categories -->
        <div class="mt-12">
          <h3 class="text-xl font-bold mb-4">Categorías</h3>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="cat in categories" 
              :key="cat"
              @click="filterByCategory(cat)"
              class="px-4 py-2 bg-white rounded-full text-sm hover:bg-primary hover:text-white transition-colors"
              :class="selectedCategory === cat ? 'bg-primary text-white' : ''"
            >
              {{ cat }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const api = useApi()

const featuredPost = ref<any>(null)
const posts = ref<any[]>([])
const categories = ref<string[]>([])
const selectedCategory = ref('')
const loading = ref(true)

const filteredPosts = computed(() => {
  if (!selectedCategory.value) return posts.value
  return posts.value.filter(p => p.category === selectedCategory.value)
})

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

const filterByCategory = (cat: string) => {
  selectedCategory.value = selectedCategory.value === cat ? '' : cat
}

const loadPosts = async () => {
  try {
    const data = await api.get('/blog?page_size=100&status=published')
    const items: any[] = Array.isArray(data) ? data : data.items || data.results || []
    posts.value = items
    if (items.length > 0) {
      featuredPost.value = items[0]
    }
    const cats = new Set(items.map((p: any) => p.category).filter(Boolean))
    categories.value = Array.from(cats) as string[]
  } catch (error) {
    console.error('Error loading blog posts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadPosts)
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>