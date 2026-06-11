<script setup lang="ts">
/**
 * Featured Packages Section
 * Packages destacados cargados desde el backend
 */
import { ref, onMounted } from 'vue'

const { fetchFeaturedTours, pending, error } = useLandingData()

// Default packages while loading
const defaultPackages = [
  {
    id: 1,
    name: 'Aventura de 7 Días',
    image: 'https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?w=600&q=80',
    duration: '7 días / 6 noches',
    price: 1299,
    originalPrice: 1599,
    badge: 'Más Popular',
    includes: ['Hotel', 'Tours', 'Transporte', 'Desayunos'],
    destinations: ['La Fortuna', 'Monteverde', 'Manuel Antonio']
  },
  {
    id: 2,
    name: 'Escapada Romántica',
    image: 'https://images.unsplash.com/photo-1540541338287-41795007eca6?w=600&q=80',
    duration: '4 días / 3 noches',
    price: 899,
    originalPrice: 1099,
    badge: 'Para Parejas',
    includes: ['Resort 5★', 'Cena romántica', 'Spa', 'Tour privado'],
    destinations: ['Guanacaste']
  },
  {
    id: 3,
    name: 'Expedición Familiar',
    image: 'https://images.unsplash.com/photo-1567696911980-2eed69a46042?w=600&q=80',
    duration: '5 días / 4 noches',
    price: 699,
    originalPrice: 849,
    badge: 'Mejor Valor',
    includes: ['Hotel familiar', 'Parques', 'Guía', 'Actividades niños'],
    destinations: ['San José', 'La Fortuna']
  }
]

const packages = ref(defaultPackages)

// Map tour from API to package format
function mapTourToPackage(tour: any) {
  return {
    id: tour.id,
    name: tour.title,
    image: tour.image_url || 'https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?w=600&q=80',
    duration: tour.duration || '1 día',
    price: tour.base_price || 99,
    originalPrice: Math.round((tour.base_price || 99) * 1.2),
    badge: tour.category || 'Tour',
    includes: tour.includes || ['Transporte', 'Guía'],
    destinations: tour.location ? [tour.location] : ['Costa Rica']
  }
}

onMounted(async () => {
  const tours = await fetchFeaturedTours(3)
  if (tours && tours.length > 0) {
    packages.value = tours.map(mapTourToPackage)
  }
})
</script>

<template>
  <section class="py-20 bg-gray-50">
    <div class="container mx-auto px-4">
      <!-- Header -->
      <div class="text-center mb-12">
        <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-700 font-semibold rounded-full text-sm mb-4">
          {{ $t('packages.badge') }}
        </span>
        <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          {{ $t('packages.title') }}
        </h2>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          {{ $t('packages.subtitle') }}
        </p>
      </div>

      <!-- Packages Grid -->
      <div class="grid md:grid-cols-3 gap-8">
        <div 
          v-for="pkg in packages" 
          :key="pkg.id"
          class="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2"
        >
          <!-- Image -->
          <div class="relative h-56 overflow-hidden">
            <NuxtImg 
              :src="pkg.image" 
              :alt="pkg.name"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
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

          <!-- Content -->
          <div class="p-6">
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ pkg.name }}</h3>
            
            <!-- Destinations -->
            <div class="flex flex-wrap gap-2 mb-4">
              <span 
                v-for="dest in pkg.destinations" 
                :key="dest"
                class="text-xs text-gray-700 bg-gray-100 px-2 py-1 rounded"
              >
                {{ dest }}
              </span>
            </div>

            <!-- Includes -->
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

            <!-- Price -->
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

            <!-- CTA -->
            <button class="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-xl transition-colors">
              {{ $t('packages.viewDetails') }}
            </button>
          </div>
        </div>
      </div>

      <!-- View All -->
      <div class="text-center mt-12">
        <NuxtLink 
          to="/paquetes" 
          class="inline-flex items-center gap-2 px-8 py-4 border-2 border-primary-600 text-primary-600 font-bold rounded-full hover:bg-primary-600 hover:text-white transition-all"
        >
          {{ $t('packages.viewAll') }}
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>
