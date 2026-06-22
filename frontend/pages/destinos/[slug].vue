<template>
  <div class="min-h-screen bg-gray-50">
    <div v-if="pending" class="container py-12 space-y-8">
      <div class="h-8 w-48 bg-gray-200 animate-pulse rounded" />
      <div class="h-80 bg-gray-200 animate-pulse rounded-3xl" />
    </div>

    <div v-else-if="error" class="container py-16 text-center">
      <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
        <AlertCircle class="w-12 h-12 text-red-400" />
      </div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">Error al cargar el destino</h3>
      <p class="text-gray-600 mb-6">No pudimos conectar con el servidor. Por favor intenta de nuevo.</p>
      <div class="flex justify-center gap-4">
        <button @click="refresh()" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors">
          Reintentar
        </button>
        <NuxtLink to="/destinos" class="px-6 py-3 bg-white text-gray-700 font-semibold rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors">
          Volver a destinos
        </NuxtLink>
      </div>
    </div>

    <div v-else-if="dest" class="container py-8">
      <!-- Breadcrumb -->
      <nav class="mb-8">
        <ol class="flex items-center gap-2 text-sm">
          <li><NuxtLink to="/" class="text-gray-500 hover:text-primary-600">Inicio</NuxtLink></li>
          <li><span class="text-gray-400">/</span></li>
          <li><NuxtLink to="/destinos" class="text-gray-500 hover:text-primary-600">Destinos</NuxtLink></li>
          <li><span class="text-gray-400">/</span></li>
          <li class="text-gray-900 font-medium">{{ dest.name }}</li>
        </ol>
      </nav>

      <!-- Hero -->
      <div class="relative rounded-3xl overflow-hidden mb-12 h-80 md:h-96">
        <img
          v-if="dest.featuredPhoto || dest.image"
          :src="dest.featuredPhoto || dest.image"
          :alt="dest.name"
          class="absolute inset-0 w-full h-full object-cover"
        />
        <div
          v-else
          class="absolute inset-0 flex items-center justify-center text-9xl"
          :class="dest.gradient"
        >
          {{ dest.icon }}
        </div>
        <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
        <div class="absolute bottom-0 left-0 right-0 p-8 md:p-12 text-white">
          <div class="flex flex-wrap items-center gap-2 mb-3">
            <span v-if="dest.region" class="inline-flex items-center gap-1 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
              <MapPin class="w-3.5 h-3.5" />
              {{ dest.region }}
            </span>
            <span v-if="dest.province" class="inline-flex items-center gap-1 px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
              {{ dest.province }}
            </span>
          </div>
          <h1 class="text-4xl md:text-5xl font-bold mt-4">{{ dest.name }}</h1>
          <p v-if="dest.description" class="text-lg mt-2 text-white/90 max-w-2xl">{{ dest.description.substring(0, 120) }}{{ dest.description.length > 120 ? '...' : '' }}</p>
        </div>
      </div>

      <div class="grid lg:grid-cols-3 gap-12">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-12">

          <!-- Full Description -->
          <section v-if="dest.description">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Acerca de {{ dest.name }}</h2>
            <p class="text-gray-600 leading-relaxed text-lg whitespace-pre-line">{{ dest.description }}</p>
          </section>

          <!-- Highlights -->
          <section v-if="dest.highlights?.length">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🎯</span> Lo más destacado
            </h2>
            <ul class="grid sm:grid-cols-2 gap-3">
              <li
                v-for="(h, i) in dest.highlights"
                :key="i"
                class="flex items-center gap-3 bg-white p-4 rounded-xl border border-gray-100"
              >
                <div class="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm flex-shrink-0">✓</div>
                {{ h }}
              </li>
            </ul>
          </section>

          <!-- Things To Do -->
          <section v-if="dest.thingsToDo?.length">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🧗</span> Actividades principales
            </h2>
            <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              <div
                v-for="(a, i) in dest.thingsToDo"
                :key="i"
                class="p-4 bg-white rounded-xl border border-gray-100 text-center hover:shadow-md transition-shadow"
              >
                <h3 class="font-semibold text-gray-900">{{ a }}</h3>
              </div>
            </div>
          </section>

          <!-- Culture -->
          <section v-if="dest.culture">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🎭</span> Cultura
            </h2>
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-xl border border-purple-100">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.culture }}</p>
            </div>
          </section>

          <!-- Gastronomy -->
          <section v-if="dest.gastronomy">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🍽️</span> Gastronomía
            </h2>
            <div class="bg-gradient-to-r from-amber-50 to-orange-50 p-6 rounded-xl border border-amber-100">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.gastronomy }}</p>
            </div>
          </section>

          <!-- History -->
          <section v-if="dest.history">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>📜</span> Historia
            </h2>
            <div class="bg-gradient-to-r from-stone-50 to-yellow-50 p-6 rounded-xl border border-stone-200">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.history }}</p>
            </div>
          </section>

          <!-- Best Time -->
          <section v-if="dest.bestTime">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>📅</span> Mejor época para visitar
            </h2>
            <div class="bg-gradient-to-r from-primary-50 to-emerald-50 p-6 rounded-xl border border-primary-100">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.bestTime }}</p>
            </div>
          </section>

          <!-- Weather -->
          <section v-if="dest.weatherInfo">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>☀️</span> Clima
            </h2>
            <div class="bg-gradient-to-r from-sky-50 to-blue-50 p-6 rounded-xl border border-sky-100">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.weatherInfo }}</p>
            </div>
          </section>

          <!-- Getting There -->
          <section v-if="dest.gettingThere">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🚗</span> Cómo llegar
            </h2>
            <div class="bg-gradient-to-r from-gray-50 to-slate-50 p-6 rounded-xl border border-gray-200">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.gettingThere }}</p>
            </div>
          </section>

          <!-- Local Tips -->
          <section v-if="dest.localTips">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>💡</span> Consejos locales
            </h2>
            <div class="bg-gradient-to-r from-teal-50 to-emerald-50 p-6 rounded-xl border border-teal-100">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.localTips }}</p>
            </div>
          </section>

          <!-- Safety -->
          <section v-if="dest.safetyInfo">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🛡️</span> Seguridad
            </h2>
            <div class="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-xl border border-red-100">
              <p class="text-gray-700 leading-relaxed whitespace-pre-line">{{ dest.safetyInfo }}</p>
            </div>
          </section>

          <!-- Gallery -->
          <section v-if="dest.gallery?.length">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>📸</span> Galería
            </h2>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <img
                v-for="(img, i) in dest.gallery"
                :key="i"
                :src="img"
                :alt="`${dest.name} - Imagen ${i + 1}`"
                class="w-full h-48 object-cover rounded-xl hover:scale-105 transition-transform"
              />
            </div>
          </section>

          <!-- Videos -->
          <section v-if="dest.videos?.length">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🎥</span> Videos
            </h2>
            <div class="grid sm:grid-cols-2 gap-4">
              <div v-for="(video, i) in dest.videos" :key="i" class="aspect-video rounded-xl overflow-hidden">
                <iframe
                  :src="video"
                  class="w-full h-full"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                />
              </div>
            </div>
          </section>

          <!-- Map -->
          <section v-if="dest.latitude && dest.longitude">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span>🗺️</span> Ubicación
            </h2>
            <div class="rounded-xl overflow-hidden h-80 border border-gray-200">
              <iframe
                width="100%"
                height="100%"
                frameborder="0"
                style="border:0"
                :src="`https://www.google.com/maps/embed/v1/place?key=&q=${dest.latitude},${dest.longitude}&zoom=${dest.zoom || 12}`"
                allowfullscreen
              />
            </div>
          </section>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Quick Info -->
          <div class="bg-white rounded-xl p-6 border border-gray-100">
            <h3 class="font-bold text-gray-900 mb-4">Información rápida</h3>
            <dl class="space-y-3 text-sm">
              <div v-if="dest.country" class="flex justify-between">
                <dt class="text-gray-500">País</dt>
                <dd class="font-medium text-gray-900">{{ dest.country }}</dd>
              </div>
              <div v-if="dest.region" class="flex justify-between">
                <dt class="text-gray-500">Región</dt>
                <dd class="font-medium text-gray-900">{{ dest.region }}</dd>
              </div>
              <div v-if="dest.province" class="flex justify-between">
                <dt class="text-gray-500">Provincia</dt>
                <dd class="font-medium text-gray-900">{{ dest.province }}</dd>
              </div>
              <div v-if="dest.canton" class="flex justify-between">
                <dt class="text-gray-500">Cantón</dt>
                <dd class="font-medium text-gray-900">{{ dest.canton }}</dd>
              </div>
              <div v-if="dest.district" class="flex justify-between">
                <dt class="text-gray-500">Distrito</dt>
                <dd class="font-medium text-gray-900">{{ dest.district }}</dd>
              </div>
            </dl>
          </div>

          <!-- Practical Info -->
          <div v-if="hasPracticalInfo" class="bg-white rounded-xl p-6 border border-gray-100">
            <h3 class="font-bold text-gray-900 mb-4">Información práctica</h3>
            <dl class="space-y-3 text-sm">
              <div v-if="dest.language" class="flex justify-between">
                <dt class="text-gray-500">Idioma</dt>
                <dd class="font-medium text-gray-900">{{ dest.language }}</dd>
              </div>
              <div v-if="dest.currency" class="flex justify-between">
                <dt class="text-gray-500">Moneda</dt>
                <dd class="font-medium text-gray-900">{{ dest.currency }}</dd>
              </div>
              <div v-if="dest.timezone" class="flex justify-between">
                <dt class="text-gray-500">Zona horaria</dt>
                <dd class="font-medium text-gray-900">{{ dest.timezone }}</dd>
              </div>
              <div v-if="dest.phoneCode" class="flex justify-between">
                <dt class="text-gray-500">Código país</dt>
                <dd class="font-medium text-gray-900">{{ dest.phoneCode }}</dd>
              </div>
              <div v-if="dest.visaInfo">
                <dt class="text-gray-500 mb-1">Visa</dt>
                <dd class="font-medium text-gray-900 text-xs whitespace-pre-line">{{ dest.visaInfo }}</dd>
              </div>
              <div v-if="dest.emergencyNumbers?.length">
                <dt class="text-gray-500 mb-1">Emergencias</dt>
                <dd class="space-y-1">
                  <div v-for="(n, i) in dest.emergencyNumbers" :key="i" class="text-sm font-medium text-gray-900">{{ n }}</div>
                </dd>
              </div>
            </dl>
          </div>

          <div class="bg-gradient-to-r from-primary-600 to-emerald-600 rounded-xl p-6 text-white">
            <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
              <span>🏨</span> Hoteles en {{ dest.name }}
            </h3>
            <p class="text-white/80 text-sm mb-4">Encuentra el mejor alojamiento para tu viaje</p>
            <NuxtLink :to="`/hoteles?region=${encodeURIComponent(dest.region || '')}`" class="block text-center py-3 bg-white text-primary-700 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Ver Hoteles
            </NuxtLink>
          </div>

          <div class="bg-white rounded-xl p-6 border border-gray-100">
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

      <!-- Related -->
      <section v-if="related.length" class="mt-16">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Otros destinos que te pueden gustar</h2>
        <div class="grid md:grid-cols-3 gap-6">
          <NuxtLink
            v-for="r in related"
            :key="r.slug"
            :to="`/destinos/${r.slug}`"
            class="group"
          >
            <div class="relative h-40 rounded-xl overflow-hidden mb-3">
              <img
                v-if="r.image"
                :src="r.image"
                :alt="r.name"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-5xl" :class="r.gradient">
                {{ r.icon }}
              </div>
              <div class="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors" />
            </div>
            <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{{ r.name }}</h3>
            <p class="text-sm text-gray-500">{{ r.location }}</p>
          </NuxtLink>
        </div>
      </section>
    </div>

    <div v-else class="container py-16 text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">Destino no encontrado</h1>
      <p class="text-gray-600 mb-6">El destino que buscas no existe o ha sido eliminado.</p>
      <NuxtLink to="/destinos" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700">
        Ver todos los destinos
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MapPin, AlertCircle } from 'lucide-vue-next'
import type { Destination } from '~/types'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const { data: destData, pending, error, refresh } = useFetch<Destination>(
  () => `${apiBase}/destinations/${route.params.slug}`,
  { default: () => null as Destination | null, key: route.params.slug as string }
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

const dest = computed(() => {
  const d = destData.value
  if (!d) return null
  return {
    ...d,
    icon: icons[d.region || ''] || '🌎',
    gradient: gradients[d.region || ''] || 'bg-gradient-to-br from-gray-500 to-gray-700',
    featuredPhoto: d.featured_photo,
    thingsToDo: d.things_to_do || [],
    bestTime: d.best_time,
    weatherInfo: d.weather_info,
    gettingThere: d.getting_there,
    localTips: d.local_tips,
    safetyInfo: d.safety_info,
    phoneCode: d.phone_code,
    visaInfo: d.visa_info,
    emergencyNumbers: d.emergency_numbers || [],
    seoTitle: d.seo_title,
    seoDescription: d.seo_description,
    seoKeywords: d.seo_keywords || []
  }
})

const hasPracticalInfo = computed(() =>
  !!(
    dest.value?.language ||
    dest.value?.currency ||
    dest.value?.timezone ||
    dest.value?.phoneCode ||
    dest.value?.visaInfo ||
    dest.value?.emergencyNumbers?.length
  )
)

const related = computed(() => {
  if (!dest.value) return []
  const sameRegion = allDestinations.value.filter(
    (d) => d.region === dest.value?.region && d.slug !== dest.value?.slug
  )
  return sameRegion.slice(0, 3).map((d) => ({
    name: d.name,
    slug: d.slug,
    image: d.image,
    icon: icons[d.region || ''] || '🌎',
    gradient: gradients[d.region || ''] || 'bg-gradient-to-br from-gray-500 to-gray-700',
    location: [d.province, d.region].filter(Boolean).join(', ')
  }))
})

const { data: allData } = useFetch<Destination[]>(
  () => `${apiBase}/destinations`,
  { default: () => [], key: 'destinos-all' }
)
// If allData fails, related section simply stays empty
const allDestinations = computed(() => allData.value || [])

useSeo({
  title: computed(() => dest.value?.name ? `${dest.value.name} | Costa Rica Travel` : 'Destino'),
  description: computed(() => dest.value?.description || ''),
  ogType: 'website'
})
</script>
