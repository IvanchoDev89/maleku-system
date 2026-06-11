<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({
  title: 'Paquetes',
  description: 'Paquetes todo incluido para tu viaje a Costa Rica'
})

const { fetchFeaturedTours, pending } = useLandingData()

interface Package {
  id: number
  name: string
  image: string
  duration: string
  price: number
  originalPrice: number
  badge: string
  includes: string[]
  destinations: string[]
}

const packages = ref<Package[]>([])
const error = ref<string | null>(null)

onMounted(async () => {
  const tours = await fetchFeaturedTours(20)
  if (tours && tours.length > 0) {
    packages.value = tours.map((tour: any) => ({
      id: tour.id,
      name: tour.title,
      image: tour.image_url || 'https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?w=600&q=80',
      duration: tour.duration || '1 día',
      price: tour.base_price || 99,
      originalPrice: Math.round((tour.base_price || 99) * 1.2),
      badge: tour.category || 'Tour',
      includes: tour.includes || ['Transporte', 'Guía'],
      destinations: tour.location ? [tour.location] : ['Costa Rica']
    }))
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container mx-auto px-4">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ $t('packages.title') }}</h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">{{ $t('packages.subtitle') }}</p>
      </div>

      <div v-if="pending" class="text-center py-16">
        <div class="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p class="text-gray-500">Cargando paquetes...</p>
      </div>

      <div v-else-if="error" class="text-center py-16">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <div v-else-if="packages.length === 0" class="text-center py-16">
        <p class="text-gray-500">No hay paquetes disponibles actualmente.</p>
      </div>

      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div
          v-for="pkg in packages"
          :key="pkg.id"
          class="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2"
        >
          <div class="relative h-56 overflow-hidden">
            <NuxtImg
              :src="pkg.image"
              :alt="pkg.name"
              class="w-full h-full object-cover hover:scale-110 transition-transform duration-500"
              width="600"
              height="400"
              format="webp"
              loading="lazy"
            />
            <div class="absolute top-4 left-4">
              <span class="px-3 py-1 bg-primary-600 text-white text-xs font-bold rounded-full">
                {{ pkg.badge }}
              </span>
            </div>
            <div class="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium">
              {{ pkg.duration }}
            </div>
          </div>

          <div class="p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ pkg.name }}</h3>

            <div class="flex flex-wrap gap-2 mb-4">
              <span
                v-for="dest in pkg.destinations"
                :key="dest"
                class="text-xs text-gray-700 bg-gray-100 px-2 py-1 rounded"
              >
                {{ dest }}
              </span>
            </div>

            <ul class="space-y-1 mb-6">
              <li
                v-for="item in pkg.includes"
                :key="item"
                class="flex items-center gap-2 text-sm text-gray-700"
              >
                <span class="text-green-500">✓</span>
                {{ item }}
              </li>
            </ul>

            <div class="flex items-end justify-between mb-4">
              <div>
                <div class="text-sm text-gray-700 line-through">${{ pkg.originalPrice }}</div>
                <div class="text-3xl font-bold text-primary-600">${{ pkg.price }}</div>
                <div class="text-xs text-gray-600">por persona</div>
              </div>
              <div class="text-right text-sm text-green-600 font-medium">
                Ahorra ${{ pkg.originalPrice - pkg.price }}
              </div>
            </div>

            <button class="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-xl transition-colors">
              {{ $t('packages.viewDetails') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
