<template>
  <section class="py-20 bg-gray-50">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-600 font-semibold rounded-full text-sm mb-4">
          {{ t('destinations.badge') }}
        </span>
        <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">{{ t('destinations.title') }}</h2>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">{{ t('destinations.subtitle') }}</p>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6" aria-busy="true">
        <div v-for="i in 6" :key="i" class="relative overflow-hidden rounded-2xl aspect-[4/3] bg-gray-200 animate-pulse">
          <div class="absolute bottom-0 left-0 right-0 p-6 space-y-2">
            <div class="h-6 bg-gray-300 rounded w-1/2"></div>
            <div class="h-4 bg-gray-300 rounded w-3/4"></div>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="dest in destinations"
          :key="dest.slug"
          :to="`/destinos/${dest.slug}`"
          class="group relative overflow-hidden rounded-2xl aspect-[4/3] focus:outline-none focus:ring-2 focus:ring-primary-500"
          :aria-label="t(`destinations.items.${dest.slug}.ariaLabel`)"
        >
          <NuxtImg
            :src="dest.image"
            :alt="t(`destinations.items.${dest.slug}.imageAlt`)"
            class="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            loading="lazy"
            width="400"
            height="300"
            format="webp"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
          <div class="absolute bottom-0 left-0 right-0 p-6">
            <h3 class="text-2xl font-bold text-white mb-1">{{ dest.name }}</h3>
            <p class="text-white/80 text-sm mb-2">{{ t(`destinations.items.${dest.slug}.description`) }}</p>
            <div class="flex items-center gap-2 text-white/70 text-sm">
              <span>{{ t(`destinations.items.${dest.slug}.highlights`) }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
              </svg>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
// @ts-ignore - Module resolution handled by Nuxt
import { DEFAULT_IMAGES } from '~/config/constants'
// @ts-ignore - Auto-imported composable
import { useLandingData } from '~/composables/useLandingData'

const { t } = useI18n()
const { fetchDestinations } = useLandingData()
const loading = ref(true)

// Destinations data structure - descriptions now use i18n keys
const baseDestinations = [
  { slug: 'guanacaste', name: 'Guanacaste', image: DEFAULT_IMAGES.destinations.guanacaste },
  { slug: 'la-fortuna', name: 'La Fortuna', image: DEFAULT_IMAGES.destinations.laFortuna },
  { slug: 'monteverde', name: 'Monteverde', image: DEFAULT_IMAGES.destinations.monteverde },
  { slug: 'manuel-antonio', name: 'Manuel Antonio', image: DEFAULT_IMAGES.destinations.manuelAntonio },
  { slug: 'caribe', name: 'Caribe Sur', image: DEFAULT_IMAGES.destinations.caribe },
  { slug: 'valle-central', name: 'Valle Central', image: DEFAULT_IMAGES.destinations.valleCentral }
]

const destinations = ref([...baseDestinations])

onMounted(async () => {
  try {
    const apiDestinations = await fetchDestinations(6)
    if (apiDestinations?.length > 0) {
      destinations.value = apiDestinations.map((dest: any) => ({
        slug: dest.slug,
        name: dest.name,
        image: dest.image || dest.image_url || DEFAULT_IMAGES.generic.tour
      }))
    }
  } catch (error) {
    console.error('Error fetching destinations:', error)
  } finally {
    loading.value = false
  }
})
</script>
