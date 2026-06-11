<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Loading -->
      <div v-if="pending" class="space-y-8">
        <div class="h-8 w-48 bg-gray-200 animate-pulse rounded"></div>
        <div class="h-80 bg-gray-200 animate-pulse rounded-3xl"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-16">
          <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle class="w-12 h-12 text-red-400" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Error al cargar el destino</h3>
          <p class="text-gray-600 mb-6">Por favor intenta de nuevo más tarde.</p>
          <NuxtLink to="/destinos" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors inline-block">
            Volver a destinos
          </NuxtLink>
      </div>

      <div v-else-if="destination">
        <!-- Breadcrumb -->
        <nav class="mb-8">
          <ol class="flex items-center gap-2 text-sm">
            <li><NuxtLink to="/" class="text-gray-500 hover:text-primary-600">Inicio</NuxtLink></li>
            <li><span class="text-gray-400">/</span></li>
            <li><NuxtLink to="/destinos" class="text-gray-500 hover:text-primary-600">Destinos</NuxtLink></li>
            <li><span class="text-gray-400">/</span></li>
            <li class="text-gray-900 font-medium">{{ destination.name }}</li>
          </ol>
        </nav>

        <!-- Hero -->
        <div class="relative rounded-3xl overflow-hidden mb-12 h-80 md:h-96">
          <div class="absolute inset-0 flex items-center justify-center text-9xl" :class="destination.gradient">
            {{ destination.icon }}
          </div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent"></div>
          <div class="absolute bottom-0 left-0 right-0 p-8 md:p-12 text-white">
            <span class="inline-flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm">
              <MapPin class="w-4 h-4" />
              {{ destination.region }}
            </span>
            <h1 class="text-4xl md:text-5xl font-bold mt-4">{{ destination.name }}</h1>
            <p class="text-lg mt-2 text-white/90">{{ destination.shortDesc }}</p>
          </div>
        </div>

        <!-- Content -->
        <div class="grid lg:grid-cols-3 gap-12">
          <!-- Main Content -->
          <div class="lg:col-span-2">
            <!-- Description -->
            <section class="mb-12">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Acerca de {{ destination.name }}</h2>
              <p class="text-gray-600 leading-relaxed text-lg">{{ destination.description }}</p>
            </section>

            <!-- Highlights -->
            <section class="mb-12">
              <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span>🎯</span> Lo que vas a encontrar
              </h2>
              <ul class="space-y-3 grid sm:grid-cols-2 gap-3">
                <li 
                  v-for="(highlight, index) in getHighlights()"
                  :key="index"
                  class="flex items-center gap-3 bg-white p-4 rounded-xl border border-gray-100"
                >
                  <div class="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm flex-shrink-0">✓</div>
                  {{ highlight }}
                </li>
              </ul>
            </section>

            <!-- Things to Do -->
            <section class="mb-12">
              <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span>🧗</span> Actividades Principales
              </h2>
              <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div 
                  v-for="activity in getThingsToDo()"
                  :key="activity.name"
                  class="p-4 bg-white rounded-xl border border-gray-100 text-center hover:shadow-md transition-shadow"
                >
                  <div class="text-3xl mb-2">{{ activity.icon }}</div>
                  <h3 class="font-semibold text-gray-900">{{ activity.name }}</h3>
                  <p class="text-sm text-gray-600 mt-1">{{ activity.desc }}</p>
                </div>
              </div>
            </section>

            <!-- Best Time -->
            <section class="mb-12">
              <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span>📅</span> Mejor Época para Visitar
              </h2>
              <div class="bg-gradient-to-r from-primary-50 to-emerald-50 p-6 rounded-xl border border-primary-100">
                <p class="text-gray-700 leading-relaxed">{{ getBestTime() }}</p>
              </div>
            </section>

            <!-- Weather Info -->
            <section class="mb-12">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">☀️ Clima</h2>
              <div class="grid sm:grid-cols-4 gap-4">
                <div class="bg-white p-4 rounded-xl border border-gray-100 text-center">
                  <div class="text-3xl mb-2">🌡️</div>
                  <p class="text-sm text-gray-500">Temperatura</p>
                  <p class="font-bold text-gray-900">22-32°C</p>
                </div>
                <div class="bg-white p-4 rounded-xl border border-gray-100 text-center">
                  <div class="text-3xl mb-2">🌧️</div>
                  <p class="text-sm text-gray-500">Lluvias</p>
                  <p class="font-bold text-gray-900">May-Nov</p>
                </div>
                <div class="bg-white p-4 rounded-xl border border-gray-100 text-center">
                  <div class="text-3xl mb-2">🏖️</div>
                  <p class="text-sm text-gray-500">Mejor época</p>
                  <p class="font-bold text-gray-900">Dic-Abr</p>
                </div>
                <div class="bg-white p-4 rounded-xl border border-gray-100 text-center">
                  <div class="text-3xl mb-2">🌊</div>
                  <p class="text-sm text-gray-500">Oleaje</p>
                  <p class="font-bold text-gray-900">Variable</p>
                </div>
              </div>
            </section>
          </div>

          <!-- Sidebar -->
          <div>
            <!-- Quick Info -->
            <div class="bg-white rounded-xl p-6 mb-6 border border-gray-100">
              <h3 class="font-bold text-gray-900 mb-4">Información Rápida</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-gray-500">Región</span>
                  <span class="font-medium text-gray-900">{{ destination.region }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-500">Provincia</span>
                  <span class="font-medium text-gray-900">{{ destination.province }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-500">Clima</span>
                  <span class="font-medium text-gray-900">Tropical</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-500">Tipo</span>
                  <span class="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                    {{ destination.is_featured ? '⭐ Destacado' : 'Tourístico' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Hotels CTA -->
            <div class="bg-gradient-to-r from-primary-600 to-emerald-600 rounded-xl p-6 text-white">
              <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
                <span>🏨</span> Hoteles en {{ destination.name }}
              </h3>
              <p class="text-white/80 text-sm mb-4">Encuentra el mejor alojamiento para tu viaje</p>
              <NuxtLink :to="`/hoteles?region=${encodeURIComponent(destination.region)}`" class="block text-center py-3 bg-white text-primary-700 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Ver Hoteles
              </NuxtLink>
            </div>

            <!-- Tours CTA -->
            <div class="mt-4 bg-white rounded-xl p-6 border border-gray-100">
              <h3 class="font-bold text-gray-900 mb-2 flex items-center gap-2">
                <span>🗺️</span> Tours en la zona
              </h3>
              <p class="text-gray-600 text-sm mb-4">Reserva experiencias únicas</p>
              <NuxtLink to="/tours" class="block text-center py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors">
                Ver Tours
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Related Destinations -->
        <section class="mt-16">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Otros Destinos que Te Pueden Gustar</h2>
          <div class="grid md:grid-cols-3 gap-6">
            <NuxtLink 
              v-for="related in relatedDestinations"
              :key="related.slug"
              :to="`/destinos/${related.slug}`"
              class="group"
            >
              <div class="relative h-40 rounded-xl overflow-hidden mb-3">
                <div class="w-full h-full flex items-center justify-center text-5xl" :class="related.gradient">
                  {{ related.icon }}
                </div>
                <div class="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors"></div>
              </div>
              <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{{ related.name }}</h3>
              <p class="text-sm text-gray-500">{{ related.region }}</p>
            </NuxtLink>
          </div>
        </section>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-16">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">Destino no encontrado</h1>
        <p class="text-gray-600 mb-6">El destino que buscas no existe o ha sido eliminado.</p>
        <NuxtLink to="/destinos" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700">
          Ver todos los destinos
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MapPin } from 'lucide-vue-next'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const slug = route.params.slug

const { data: destination, pending, error } = useFetch(
  () => `${apiBase}/destinations/${slug}`,
  {
    default: () => null
  }
)

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

const computedDestination = computed(() => {
  if (!destination.value) return null
  return {
    ...destination.value,
    slug: destination.value.slug || destination.value.name?.toLowerCase().replace(/\s+/g, '-'),
    shortDesc: destination.value.description?.substring(0, 80) + '...',
    icon: icons[destination.value.region] || '🌎',
    gradient: gradients[destination.value.region] || 'bg-gradient-to-br from-gray-500 to-gray-700'
  }
})

const getHighlights = () => {
  const desc = computedDestination.value?.description || ''
  const highlights = [
    'Paisajes espectaculares',
    'Cultura local única',
    'Gastronomía típica',
    'Actividades al aire libre',
    'Flora y fauna endémica',
    'Experiencias auténticas'
  ]
  return highlights.slice(0, 6)
}

const getThingsToDo = () => {
  return [
    { icon: '🏖️', name: 'Playas', desc: 'Las mejores playas' },
    { icon: '🥾', name: 'Senderismo', desc: 'Rutas naturales' },
    { icon: '📸', name: 'Fotografía', desc: 'Paisajes únicos' },
    { icon: '🍽️', name: 'Gastronomía', desc: 'Comida local' },
    { icon: '🛶', name: 'Aventuras', desc: 'Actividades acuáticas' },
    { icon: ' Wildlife', name: 'Fauna', desc: 'Avistamiento' }
  ]
}

const getBestTime = () => {
  return 'La mejor época para visitar es de diciembre a abril, durante la estación seca. Los meses de marzo y abril son los más cálidos. De mayo a noviembre es la estación lluviosa, pero las lluvias son principalmente por la tarde y no arruinan tus planes.'
}

const relatedDestinations = computed(() => {
  return [
    { name: 'La Fortuna', slug: 'la-fortuna', icon: '🌋', gradient: 'bg-gradient-to-br from-green-500 to-primary-600', region: 'Norte' },
    { name: 'Monteverde', slug: 'monteverde', icon: '☁️', gradient: 'bg-gradient-to-br from-slate-500 to-slate-700', region: 'Norte' },
    { name: 'Manuel Antonio', slug: 'manuel-antonio', icon: '🦝', gradient: 'bg-gradient-to-br from-emerald-500 to-cyan-600', region: 'Pacífico Central' }
  ]
})

useSeo({
  title: computed(() => computedDestination.value?.name ? `${computedDestination.value.name} | Costa Rica Travel` : 'Destino'),
  description: computed(() => computedDestination.value?.description || ''),
  ogType: 'website'
})
</script>