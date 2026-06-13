<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Destinos en Costa Rica</h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">Explora las regiones más impresionantes del país, desde playas paradisíacas hasta volcanes activos</p>
      </div>

      <!-- Filter -->
      <div class="flex flex-wrap justify-center gap-3 mb-12">
        <button
          v-for="region in regions"
          :key="region"
          @click="selectedRegion = selectedRegion === region ? '' : region"
          class="px-5 py-2.5 rounded-full transition-all font-medium text-sm"
          :class="selectedRegion === region ? 'bg-primary-600 text-white shadow-md' : 'bg-white text-gray-700 hover:bg-primary-50 border border-gray-200'"
        >
          {{ region }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="pending" class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="i in 6" :key="i" class="rounded-2xl overflow-hidden">
          <div class="h-64 bg-gray-200 animate-pulse"></div>
          <div class="p-6 space-y-3">
            <div class="h-6 bg-gray-200 rounded w-3/4 animate-pulse"></div>
            <div class="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
          </div>
        </div>
      </div>

      <!-- Destinations Grid -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <NuxtLink
          v-for="dest in filteredDestinations"
          :key="dest.id"
          :to="`/destinos/${dest.slug || dest.name.toLowerCase().replace(/\s+/g, '-')}`"
          class="group"
        >
          <div class="relative rounded-2xl overflow-hidden shadow-lg h-72">
            <div
              class="absolute inset-0 flex items-center justify-center text-8xl"
              :class="dest.gradient"
            >
              {{ dest.icon }}
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
            <div class="absolute inset-0 bg-primary-600/0 group-hover:bg-primary-600/10 transition-colors duration-300"></div>
            <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
              <span class="inline-flex items-center gap-1 text-white/80 text-sm mb-2">
                <MapPin class="w-4 h-4" />
                {{ dest.region }}
              </span>
              <h3 class="text-2xl font-bold group-hover:text-primary-300 transition-colors">
                {{ dest.name }}
              </h3>
              <p class="mt-2 text-white/90 text-sm line-clamp-2">{{ dest.shortDesc }}</p>
              <div class="mt-4 flex items-center justify-between">
                <span class="text-sm flex items-center gap-1">
                  <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                  {{ dest.rating }}
                </span>
                <span class="text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
                  Ver más <ArrowRight class="w-4 h-4" />
                </span>
              </div>
            </div>
          </div>
        </NuxtLink>
      </div>

      <!-- Empty State -->
      <div v-if="!pending && filteredDestinations.length === 0" class="text-center py-16">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <MapPin class="w-12 h-12 text-gray-400" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">No hay destinos en esta región</h2>
        <button @click="selectedRegion = ''" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 mt-4">
          Ver todos
        </button>
      </div>

      <!-- Info Section -->
      <div class="mt-16 bg-white rounded-2xl shadow-sm p-8">
        <h2 class="text-2xl font-bold mb-6 text-gray-900">¿Por qué visitar Costa Rica?</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4 text-4xl">
              🏔️
            </div>
            <h3 class="font-semibold mb-2 text-gray-900">Biodiversidad</h3>
            <p class="text-gray-600 text-sm">4% de la biodiversidad mundial en un territorio pequeño</p>
          </div>
          <div class="text-center">
            <div class="w-20 h-20 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4 text-4xl">
              ☀️
            </div>
            <h3 class="font-semibold mb-2 text-gray-900">Clima Perfecto</h3>
            <p class="text-gray-600 text-sm">Temperaturas entre 20-30°C todo el año</p>
          </div>
          <div class="text-center">
            <div class="w-20 h-20 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4 text-4xl">
              🛡️
            </div>
            <h3 class="font-semibold mb-2 text-gray-900">Seguridad</h3>
            <p class="text-gray-600 text-sm">Uno de los países más seguros de Latinoamérica</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MapPin, Star, ArrowRight } from 'lucide-vue-next'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const selectedRegion = ref('')

const { data: apiData, pending } = useFetch(
  () => `${apiBase}/destinations`,
  {
    default: () => []
  }
)

const destinations = computed(() => {
  const icons: Record<string, string> = {
    'Pacífico Norte': '🏖️',
    'Norte': '🌋',
    'Pacífico Central': '🦝',
    'Valle Central': '🏛️',
    'Caribe': '🌴',
    'Pacífico Sur': '🌿'
  }
  const gradients: Record<string, string> = {
    'Pacífico Norte': 'bg-gradient-to-br from-yellow-400 to-orange-500',
    'Norte': 'bg-gradient-to-br from-green-500 to-primary-600',
    'Pacífico Central': 'bg-gradient-to-br from-emerald-500 to-cyan-600',
    'Valle Central': 'bg-gradient-to-br from-amber-400 to-yellow-500',
    'Caribe': 'bg-gradient-to-br from-primary-400 to-emerald-500',
    'Pacífico Sur': 'bg-gradient-to-br from-green-600 to-primary-700'
  }

  return (apiData.value || []).map((d: any) => ({
    id: d.id,
    name: d.name,
    slug: d.slug || d.name.toLowerCase().replace(/\s+/g, '-'),
    region: d.region,
    description: d.description,
    shortDesc: d.description?.substring(0, 80) + '...',
    icon: icons[d.region] || '🌎',
    gradient: gradients[d.region] || 'bg-gradient-to-br from-gray-500 to-gray-700',
    rating: '4.8',
    is_featured: d.is_featured
  }))
})

const regions = computed(() => {
  const unique = new Set(destinations.value.map((d: any) => d.region).filter(Boolean))
  return Array.from(unique).sort()
})

const filteredDestinations = computed(() => {
  if (!selectedRegion.value) return destinations.value
  return destinations.value.filter((d: any) => d.region === selectedRegion.value)
})

useSeo({
  title: 'Destinos en Costa Rica',
  description: 'Explora las mejores regiones de Costa Rica: Guanacaste, Arenal, Monteverde, Manuel Antonio, Caribe y Valle Central. Playas, volcanes y naturaleza.',
  keywords: 'destinos Costa Rica, Guanacaste, Arenal, Monteverde, Manuel Antonio, Caribe, volcanes, playas',
  ogType: 'website'
})
</script>
