<template>
  <section class="py-20 bg-gradient-to-br from-gray-50 to-gray-100">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-600 font-semibold rounded-full text-sm mb-4">
          {{ t('experiences.badge') }}
        </span>
        <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">{{ t('experiences.title') }}</h2>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">{{ t('experiences.subtitle') }}</p>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="grid md:grid-cols-2 lg:grid-cols-4 gap-6" aria-busy="true" aria-label="Cargando experiencias">
        <div v-for="i in 4" :key="i" class="bg-white rounded-2xl overflow-hidden shadow-sm">
          <div class="h-48 bg-gray-200 animate-pulse" />
          <div class="p-5 space-y-3">
            <div class="h-5 bg-gray-200 rounded w-3/4 animate-pulse" />
            <div class="h-4 bg-gray-200 rounded w-full animate-pulse" />
            <div class="flex justify-between">
              <div class="h-4 bg-gray-200 rounded w-16 animate-pulse" />
              <div class="h-4 bg-gray-200 rounded w-12 animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <NuxtLink
          v-for="exp in experiences"
          :key="exp.slug"
          :to="`/tours?category=${exp.slug}`"
          class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
          :aria-label="t(`experiences.items.${exp.slug}.ariaLabel`)"
        >
          <div class="relative h-48 overflow-hidden">
            <NuxtImg
              :src="exp.image"
              :alt="t(`experiences.items.${exp.slug}.imageAlt`)"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              loading="lazy"
              width="400"
              height="300"
              format="webp"
            />
            <div class="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-primary-600">
              {{ t(`experiences.items.${exp.slug}.duration`) }}
            </div>
          </div>
          <div class="p-5">
            <h3 class="font-bold text-gray-900 mb-2">{{ t(`experiences.items.${exp.slug}.name`) }}</h3>
            <p class="text-gray-600 text-sm mb-3">{{ t(`experiences.items.${exp.slug}.description`) }}</p>
            <div class="flex items-center justify-between">
              <span class="text-primary-600 font-bold">{{ exp.price }}</span>
              <span class="text-sm text-gray-500">{{ t(`experiences.items.${exp.slug}.difficulty`) }}</span>
            </div>
          </div>
        </NuxtLink>
      </div>

      <div class="text-center mt-12">
        <NuxtLink
          to="/tours"
          class="inline-flex items-center gap-2 px-6 py-3 border-2 border-primary-600 text-primary-600 font-semibold rounded-full hover:bg-primary-600 hover:text-white transition-all focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          {{ t('common.seeAll') }}
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
          </svg>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const loading = ref(true)

const experiences = [
  {
    slug: 'adventure',
    image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&q=80',
    price: '$60+'
  },
  {
    slug: 'nature',
    image: 'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=600&q=80',
    price: '$45+'
  },
  {
    slug: 'beach',
    image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=600&q=80',
    price: '$50+'
  },
  {
    slug: 'culture',
    image: 'https://images.unsplash.com/photo-1588708885923-98c04a8e4c3f?w=600&q=80',
    price: '$40+'
  }
]

onMounted(() => {
  // Simulate data loading for better UX
  setTimeout(() => {
    loading.value = false
  }, 400)
})
</script>
