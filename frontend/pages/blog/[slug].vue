<template>
  <div class="min-h-screen bg-white py-12">
    <div class="container max-w-4xl">
      <!-- Breadcrumb -->
      <nav class="mb-8">
        <ol class="flex items-center gap-2 text-sm">
          <li><NuxtLink to="/" class="text-gray-500 hover:text-primary">Inicio</NuxtLink></li>
          <li><span class="text-gray-400">/</span></li>
          <li><NuxtLink to="/blog" class="text-gray-500 hover:text-primary">Blog</NuxtLink></li>
          <li><span class="text-gray-400">/</span></li>
          <li class="text-primary font-medium">{{ post?.title }}</li>
        </ol>
      </nav>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Cargando artículo...</p>
      </div>

      <template v-else-if="!post">
        <div class="text-center py-12">
          <p class="text-gray-500">Artículo no encontrado</p>
          <NuxtLink to="/blog" class="text-primary hover:underline mt-2 inline-block">Volver al blog</NuxtLink>
        </div>
      </template>

      <template v-else>
      <!-- Article Header -->
      <header class="mb-8">
        <span class="inline-block px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
          {{ post?.category }}
        </span>
        <h1 class="text-4xl md:text-5xl font-bold mt-4">{{ post?.title }}</h1>

        <div class="flex items-center gap-6 mt-6 text-gray-500">
          <span class="flex items-center gap-2">
            <span class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white">A</span>
            {{ post?.author }}
          </span>
          <span>📅 {{ formatDate(post?.published_at) }}</span>
          <span>👁️ {{ post?.views_count }} vistas</span>
        </div>
      </header>

      <!-- Featured Image -->
      <div class="aspect-video bg-gradient-to-br from-primary to-primary-700 rounded-2xl mb-8 flex items-center justify-center">
        <span class="text-8xl">📝</span>
      </div>

      <!-- Article Content -->
      <article class="prose prose-lg max-w-none">
        <p class="lead text-xl text-gray-600 mb-8">{{ post?.excerpt }}</p>

        <div v-html="sanitizeHtml(post?.content)"></div>
      </article>

      <!-- Tags -->
      <div class="mt-12 pt-8 border-t">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in post?.tags"
            :key="tag"
            class="px-4 py-2 bg-gray-100 rounded-full text-sm"
          >
            #{{ tag }}
          </span>
        </div>
      </div>

      <!-- Share -->
      <div class="mt-8 flex items-center gap-4">
        <span class="text-gray-500">Compartir:</span>
        <button class="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center hover:bg-blue-600">F</button>
        <button class="w-10 h-10 bg-sky-500 text-white rounded-full flex items-center justify-center hover:bg-sky-600">T</button>
        <button class="w-10 h-10 bg-green-500 text-white rounded-full flex items-center justify-center hover:bg-green-600">W</button>
      </div>

      <!-- Related Posts -->
      <section class="mt-16">
        <h3 class="text-2xl font-bold mb-6">Artículos Relacionados</h3>
        <div class="grid md:grid-cols-3 gap-6">
          <NuxtLink
            v-for="related in relatedPosts"
            :key="related.id"
            :to="`/blog/${related.slug}`"
            class="group"
          >
            <div class="aspect-video bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
              <span class="text-3xl">📄</span>
            </div>
            <h4 class="font-semibold group-hover:text-primary transition-colors">{{ related.title }}</h4>
          </NuxtLink>
        </div>
      </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import DOMPurify from 'dompurify'

const sanitizeHtml = (html: string | null | undefined): string => {
  if (!html) return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'h2', 'h3', 'h4', 'p', 'a', 'ul', 'ol', 'li', 'img', 'blockquote',
      'code', 'pre', 'strong', 'em', 'br', 'hr', 'figure', 'figcaption',
    ],
    ALLOWED_ATTR: ['href', 'title', 'alt', 'src', 'loading', 'class', 'target', 'rel'],
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/i,
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'svg', 'math'],
  })
}

const route = useRoute()
const api = useApi()
const slug = route.params.slug as string

const post = ref<any>(null)
const relatedPosts = ref<any[]>([])
const loading = ref(true)

const formatDate = (date: string | undefined) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

const loadPost = async () => {
  try {
    const data = await api.get(`/blog?page_size=100&status=published`)
    const items: any[] = Array.isArray(data) ? data : data.items || data.results || []
    const found = items.find((p: any) => p.slug === slug)
    if (found) {
      post.value = found
    }
    relatedPosts.value = items.filter((p: any) => p.id !== found?.id).slice(0, 3)
  } catch (error) {
    console.error('Error loading blog post:', error)
  } finally {
    loading.value = false
  }
}

watch(post, (newPost) => {
  if (!newPost) return
  useSeo({
    title: newPost.title,
    description: newPost.excerpt,
    keywords: newPost.tags?.join(', '),
    ogType: 'article',
    ogImage: newPost.featured_image || 'https://costaricatravel.dev/images/blog-default.jpg',
    canonical: `https://costaricatravel.dev/blog/${slug}`
  })
  useJsonLd({
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": newPost.title,
    "description": newPost.excerpt,
    "url": `https://costaricatravel.dev/blog/${slug}`,
    "datePublished": newPost.published_at,
    "author": {
      "@type": "Organization",
      "name": newPost.author
    },
    "articleSection": newPost.category,
    "keywords": newPost.tags?.join(', ')
  })
})

onMounted(loadPost)
</script>

<style>
.prose h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #1a1a2e;
}
.prose p {
  margin-bottom: 1.5rem;
  line-height: 1.8;
}
.prose ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1.5rem;
}
.prose li {
  margin-bottom: 0.5rem;
}
</style>
