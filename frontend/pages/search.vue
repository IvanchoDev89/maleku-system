<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container py-8">
      <NuxtLink to="/" class="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6 transition-colors">
        <ArrowLeft class="w-4 h-4" />
        <span>Volver al inicio</span>
      </NuxtLink>

      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Resultados de búsqueda</h1>
        <p v-if="query" class="text-gray-600">
          Mostrando resultados para "<span class="font-medium text-gray-900">{{ query }}</span>"
        </p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-4 mb-8">
        <div class="flex gap-4">
          <div class="relative flex-1">
            <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              v-model="searchInput"
              type="text"
              placeholder="Buscar hoteles, tours, destinos..."
              class="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-gray-900"
              @keyup.enter="performSearch"
            />
          </div>
          <button
            @click="performSearch"
            class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors flex items-center gap-2"
          >
            <Search class="w-5 h-5" />
            <span>Buscar</span>
          </button>
        </div>
      </div>

      <div v-if="pending" class="grid md:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="bg-white rounded-xl overflow-hidden shadow-sm">
          <div class="h-48 bg-gray-200 animate-pulse"></div>
          <div class="p-4 space-y-3">
            <div class="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
          </div>
        </div>
      </div>

      <div v-else>
        <!-- Error State -->
        <div v-if="error" class="text-center py-16">
          <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle class="w-12 h-12 text-red-400" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Error en la búsqueda</h3>
          <p class="text-gray-600 mb-6">Por favor intenta de nuevo más tarde.</p>
          <NuxtLink to="/" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors inline-block">
            Volver al inicio
          </NuxtLink>
        </div>

        <div v-else-if="!hasResults" class="text-center py-16">
          <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Search class="w-12 h-12 text-gray-400" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900 mb-2">No se encontraron resultados</h2>
          <p class="text-gray-600 mb-6">Intenta con otros términos de búsqueda</p>
          <NuxtLink to="/" class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700">
            <ArrowLeft class="w-4 h-4" />
            Volver al inicio
          </NuxtLink>
        </div>

        <div v-else class="space-y-12">
          <div class="flex items-center justify-between">
            <p class="text-gray-600">
              <span class="font-bold text-gray-900">{{ totalResults }}</span> resultados encontrados
            </p>
          </div>

          <section v-if="results.properties?.length">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Building2 class="w-6 h-6 text-primary-600" />
                Hoteles ({{ results.properties.length }})
              </h2>
              <NuxtLink to="/hoteles" class="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
                Ver todos <ArrowRight class="w-4 h-4" />
              </NuxtLink>
            </div>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <NuxtLink
                v-for="prop in results.properties"
                :key="prop.id"
                :to="`/hoteles/${prop.slug}`"
                class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow group"
              >
                <div class="relative h-48 overflow-hidden">
                  <NuxtImg
                    :src="prop.images?.[0] || prop.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945'"
                    :alt="prop.name"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    width="800"
                    height="400"
                    format="webp"
                    loading="lazy"
                  />
                  <div class="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg text-sm font-medium text-gray-700">
                    {{ prop.property_type || 'Hotel' }}
                  </div>
                </div>
                <div class="p-4">
                  <h3 class="font-bold text-gray-900 text-lg group-hover:text-primary-600 transition-colors">{{ prop.name }}</h3>
                  <p class="text-gray-500 text-sm mt-1 flex items-center gap-1">
                    <MapPin class="w-3 h-3" />
                    {{ prop.region || 'Costa Rica' }}
                  </p>
                  <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                    <span class="text-xl font-bold text-primary-600">${{ prop.base_price || prop.price }} <span class="text-sm font-normal text-gray-500">/noche</span></span>
                    <div class="flex items-center gap-1">
                      <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                      <span class="text-gray-700 font-medium">{{ prop.rating?.toFixed(1) || '4.5' }}</span>
                    </div>
                  </div>
                </div>
              </NuxtLink>
            </div>
          </section>

          <section v-if="results.tours?.length">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Compass class="w-6 h-6 text-primary-600" />
                Tours ({{ results.tours.length }})
              </h2>
              <NuxtLink to="/tours" class="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
                Ver todos <ArrowRight class="w-4 h-4" />
              </NuxtLink>
            </div>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <NuxtLink
                v-for="tour in results.tours"
                :key="tour.id"
                :to="`/tours/${tour.slug}`"
                class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow group"
              >
                <div class="relative h-48 overflow-hidden">
                  <NuxtImg
                    :src="tour.cover_image || tour.image || 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7'"
                    :alt="tour.name"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    width="800"
                    height="400"
                    format="webp"
                    loading="lazy"
                  />
                  <div class="absolute top-3 right-3 bg-amber-500 text-white px-2 py-1 rounded-lg text-sm font-bold">
                    {{ tour.category || 'Tour' }}
                  </div>
                </div>
                <div class="p-4">
                  <h3 class="font-bold text-gray-900 text-lg group-hover:text-primary-600 transition-colors">{{ tour.name }}</h3>
                  <p class="text-gray-500 text-sm mt-1 flex items-center gap-1">
                    <MapPin class="w-3 h-3" />
                    {{ tour.location || 'Costa Rica' }}
                  </p>
                  <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                    <span class="text-xl font-bold text-primary-600">${{ tour.price }} <span class="text-sm font-normal text-gray-500">/persona</span></span>
                    <div class="flex items-center gap-2">
                      <div class="flex items-center gap-1">
                        <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                        <span class="text-gray-700 font-medium">{{ tour.rating?.toFixed(1) || '4.5' }}</span>
                      </div>
                      <span v-if="tour.duration_hours" class="text-gray-500 text-sm flex items-center gap-1">
                        <Clock class="w-3 h-3" />
                        {{ tour.duration_hours }}h
                      </span>
                    </div>
                  </div>
                </div>
              </NuxtLink>
            </div>
          </section>

          <section v-if="results.destinations?.length">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <MapPin class="w-6 h-6 text-primary-600" />
                Destinos ({{ results.destinations.length }})
              </h2>
              <NuxtLink to="/destinos" class="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
                Ver todos <ArrowRight class="w-4 h-4" />
              </NuxtLink>
            </div>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <NuxtLink
                v-for="dest in results.destinations"
                :key="dest.id"
                :to="`/destinos/${dest.slug}`"
                class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-shadow group"
              >
                <div class="relative h-48 overflow-hidden">
                  <NuxtImg
                    :src="dest.image || 'https://images.unsplash.com/photo-1538108149393-fbbd81895907'"
                    :alt="dest.name"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    width="800"
                    height="400"
                    format="webp"
                    loading="lazy"
                  />
                  <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                  <div class="absolute bottom-4 left-4 text-white">
                    <h3 class="font-bold text-xl">{{ dest.name }}</h3>
                  </div>
                </div>
              </NuxtLink>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Search, Building2, Compass, MapPin, Star, ArrowLeft, ArrowRight, Clock } from 'lucide-vue-next'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const route = useRoute()
const router = useRouter()

const query = computed(() => route.query.q as string || '')
const searchInput = ref(query.value)

const { data: results, pending, error } = useFetch(
  () => `${apiBase}/search`,
  {
    key: 'search-results',
    query: { q: query.value },
    watch: [query],
    default: () => ({ properties: [], tours: [], destinations: [], blog: [] })
  }
)

const performSearch = () => {
  if (searchInput.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchInput.value.trim())}`)
  }
}

const hasResults = computed(() => {
  return (
    (results.value?.properties?.length || 0) > 0 ||
    (results.value?.tours?.length || 0) > 0 ||
    (results.value?.destinations?.length || 0) > 0
  )
})

const totalResults = computed(() => {
  return (
    (results.value?.properties?.length || 0) +
    (results.value?.tours?.length || 0) +
    (results.value?.destinations?.length || 0)
  )
})

useSeo({
  title: `Búsqueda: ${query.value} - Costa Rica Travel`,
  description: `Resultados de búsqueda para "${query.value}" en Costa Rica Travel`
})
</script>
