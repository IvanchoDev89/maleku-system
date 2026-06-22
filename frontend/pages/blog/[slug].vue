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
      <div v-if="pending" class="text-center py-12">
        <p class="text-gray-500">Cargando artículo...</p>
      </div>

      <template v-else-if="error">
        <div class="text-center py-12">
          <p class="text-gray-500">Error al cargar el artículo</p>
          <button @click="refresh" class="text-primary hover:underline mt-2 inline-block">Intentar de nuevo</button>
        </div>
      </template>

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
          {{ post?.category || 'Blog' }}
        </span>
        <h1 class="text-4xl md:text-5xl font-bold mt-4">{{ post?.title }}</h1>

        <div class="flex items-center gap-6 mt-6 text-gray-500">
          <span class="flex items-center gap-2">
            <span class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white">A</span>
            {{ post?.author || 'Costa Rica Travel' }}
          </span>
          <span class="flex items-center gap-2" v-if="post?.published_at">
            <Calendar class="w-4 h-4" />
            {{ formatDate(post?.published_at) }}
          </span>
          <span class="flex items-center gap-2" v-if="post?.views_count !== undefined">
            <Eye class="w-4 h-4" />
            {{ post?.views_count }} vistas
          </span>
        </div>
      </header>

      <!-- Featured Image -->
      <div v-if="post?.featured_image" class="aspect-video rounded-2xl mb-8 overflow-hidden">
        <NuxtImg
          :src="post.featured_image"
          :alt="post.title"
          class="w-full h-full object-cover"
          width="1200"
          height="675"
          format="webp"
          loading="lazy"
        />
      </div>
      <div v-else class="aspect-video bg-gradient-to-br from-primary to-primary-700 rounded-2xl mb-8 flex items-center justify-center">
        <FileText class="w-16 h-16 text-white/50" />
      </div>

      <!-- Article Content -->
      <article class="prose prose-lg max-w-none">
        <p v-if="post?.excerpt" class="lead text-xl text-gray-600 mb-8">{{ post.excerpt }}</p>

        <div v-html="sanitizeHtml(post?.content)"></div>
      </article>

      <!-- Tags -->
      <div v-if="post?.tags?.length" class="mt-12 pt-8 border-t">
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
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import DOMPurify from 'dompurify'
import { Calendar, Eye, FileText } from 'lucide-vue-next'

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
const slug = route.params.slug as string

const { data: post, pending, error, refresh } = await useAsyncData<Record<string, any> | null>(
  `blog-${slug}`,
  async () => {
    const api = useApi()
    return await api.get(`/blog/slug/${slug}`)
  },
  { default: () => null }
)

const formatDate = (date: string | undefined) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

if (post.value) {
  useSeo({
    title: post.value.title,
    description: post.value.excerpt,
    keywords: post.value.tags?.join(', '),
    ogType: 'article',
    ogImage: post.value.featured_image || 'https://costaricatravel.dev/images/blog-default.jpg',
    canonical: `https://costaricatravel.dev/blog/${slug}`
  })
  useJsonLd({
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": post.value.title,
    "description": post.value.excerpt,
    "url": `https://costaricatravel.dev/blog/${slug}`,
    "datePublished": post.value.published_at,
    "author": {
      "@type": "Organization",
      "name": post.value.author || 'Costa Rica Travel'
    },
    "articleSection": post.value.category,
    "keywords": post.value.tags?.join(', ')
  })
}
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
