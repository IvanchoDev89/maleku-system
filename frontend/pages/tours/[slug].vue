<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Loading -->
      <div v-if="pending" class="space-y-8">
        <div class="h-8 w-48 bg-gray-200 animate-pulse rounded"></div>
        <div class="h-96 bg-gray-200 animate-pulse rounded-2xl"></div>
      </div>

      <div v-else-if="tour">
        <!-- Error State -->
        <div v-if="error" class="text-center py-16">
          <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle class="w-12 h-12 text-red-400" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Error al cargar el tour</h3>
          <p class="text-gray-600 mb-6">Por favor intenta de nuevo más tarde.</p>
          <NuxtLink to="/tours" class="px-6 py-3 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 transition-colors inline-block">
            Volver a tours
          </NuxtLink>
        </div>

        <template v-else>
        <!-- Breadcrumb -->
        <nav class="mb-8">
          <ol class="flex items-center gap-2 text-sm">
            <li><NuxtLink to="/" class="text-gray-500 hover:text-teal-600">Inicio</NuxtLink></li>
            <li><span class="text-gray-400">/</span></li>
            <li><NuxtLink to="/tours" class="text-gray-500 hover:text-teal-600">Tours</NuxtLink></li>
            <li><span class="text-gray-400">/</span></li>
            <li class="text-gray-900 font-medium">{{ tour.name }}</li>
          </ol>
        </nav>

        <!-- Hero Image -->
        <div class="relative h-80 md:h-96 rounded-2xl overflow-hidden mb-8">
          <NuxtImg
            :src="tour.cover_image || 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=1200&q=80'"
            :alt="tour.name"
            class="w-full h-full object-cover"
            width="1200"
            height="600"
            format="webp"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
          <div class="absolute bottom-8 left-8 text-white">
            <span class="inline-block px-3 py-1 bg-amber-500 text-white text-sm font-bold rounded-full mb-2">
              {{ formatCategory(tour.category) }}
            </span>
            <h1 class="text-4xl font-bold">{{ tour.name }}</h1>
          </div>
        </div>

        <!-- Main Content -->
        <div class="grid lg:grid-cols-3 gap-12">
          <div class="lg:col-span-2">
            <!-- Info Row -->
            <div class="flex flex-wrap items-center gap-4 mb-6 text-gray-600">
              <div class="flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-gray-200">
                <Clock class="w-5 h-5 text-teal-600" />
                <span class="font-medium">{{ tour.duration_hours }}h</span>
              </div>
              <div class="flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-gray-200">
                <Users class="w-5 h-5 text-teal-600" />
                <span class="font-medium">Max {{ tour.max_group_size || 15 }} personas</span>
              </div>
              <div 
                class="flex items-center gap-2 px-4 py-2 rounded-full border"
                :class="difficultyColor"
              >
                <span>{{ difficultyLabel }}</span>
              </div>
              <div class="flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-gray-200">
                <MapPin class="w-5 h-5 text-teal-600" />
                <span class="font-medium">{{ tour.location }}</span>
              </div>
            </div>

            <!-- Description -->
            <section class="mb-8">
              <p class="text-gray-600 leading-relaxed text-lg">{{ tour.description || tour.short_description }}</p>
            </section>

            <!-- Includes -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">¿Qué incluye?</h2>
              <div class="grid sm:grid-cols-2 gap-4">
                <div 
                  v-for="(item, index) in getIncludes()"
                  :key="index"
                  class="flex items-center gap-3 bg-white p-4 rounded-xl border border-gray-100"
                >
                  <div class="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center text-teal-600">
                    <Check class="w-4 h-4" />
                  </div>
                  <span class="text-gray-700">{{ item }}</span>
                </div>
              </div>
            </section>

            <!-- Itinerary -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Itinerario</h2>
              <div class="space-y-4">
                <div 
                  v-for="(item, index) in getItinerary()"
                  :key="index"
                  class="flex gap-4 bg-white p-4 rounded-xl border border-gray-100"
                >
                  <div class="w-10 h-10 bg-teal-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                    {{ index + 1 }}
                  </div>
                  <div>
                    <h3 class="font-semibold text-gray-900">{{ item.time }}</h3>
                    <p class="text-gray-600">{{ item.activity }}</p>
                  </div>
                </div>
              </div>
            </section>

            <!-- What to Bring -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Qué Llevar</h2>
              <div class="flex flex-wrap gap-3">
                <span 
                  v-for="item in getWhatToBring()"
                  :key="item"
                  class="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {{ item }}
                </span>
              </div>
            </section>

            <!-- Meeting Point -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Punto de Encuentro</h2>
              <div class="bg-white p-6 rounded-xl border border-gray-100">
                <div class="flex items-start gap-4">
                  <MapPin class="w-6 h-6 text-teal-600 flex-shrink-0 mt-1" />
                  <div>
                    <p class="font-semibold text-gray-900">{{ tour.location }}</p>
                    <p class="text-gray-600 text-sm mt-1">Te recogemos en tu hotel o punto de encuentro. Confirmación 24h antes.</p>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <!-- Sidebar - Booking -->
          <div>
            <div class="sticky top-24">
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div class="text-center mb-6">
                  <span class="text-4xl font-bold text-teal-600">${{ tour.price }}</span>
                  <span class="text-gray-500">/persona</span>
                </div>

                <div class="space-y-4 mb-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Fecha</label>
                    <input
                      v-model="tourDate"
                      type="date"
                      :min="todayIso"
                      class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Personas</label>
                    <UiSelect v-model="persons" :options="personOptions" />
                  </div>
                </div>

                <button
                  class="w-full py-4 bg-gradient-to-r from-teal-600 to-emerald-600 text-white font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!tourDate"
                  @click="goToCheckout"
                >
                  Reservar Ahora
                </button>

                <p class="text-center text-gray-500 text-sm mt-4 flex items-center justify-center gap-2">
                  <Check class="w-4 h-4" />
                  Cancelación gratis hasta 24h antes
                </p>
              </div>

              <!-- Contact -->
              <div class="mt-6 p-4 bg-white rounded-xl border border-gray-100">
                <h3 class="font-semibold text-gray-900 mb-2">¿Tienes preguntas?</h3>
                <p class="text-gray-600 text-sm mb-4">Contáctanos directamente</p>
                <div class="space-y-2">
                  <a href="tel:+50688888888" class="flex items-center gap-2 text-teal-600 hover:text-teal-700">
                    <Phone class="w-4 h-4" />
                    +506 8888 8888
                  </a>
                  <a href="mailto:info@costaricatravel.dev" class="flex items-center gap-2 text-teal-600 hover:text-teal-700">
                    <Mail class="w-4 h-4" />
                    info@costaricatravel.dev
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
        </template>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-16">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">Tour no encontrado</h1>
        <p class="text-gray-600 mb-6">El tour que buscas no existe o ha sido eliminado.</p>
        <NuxtLink to="/tours" class="px-6 py-3 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700">
          Ver todos los tours
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Clock, Users, MapPin, Check, Phone, Mail } from 'lucide-vue-next'

const persons = ref('2')
const tourDate = ref('')

const personOptions = [
  { value: '1', label: '1 persona' },
  { value: '2', label: '2 personas' },
  { value: '3', label: '3 personas' },
  { value: '4', label: '4 personas' },
  { value: '5', label: '5+ personas' },
]

const todayIso = computed(() => new Date().toISOString().slice(0, 10))

const goToCheckout = () => {
  if (!tour.value || !tourDate.value) return
  const total = Number(tour.value.price) * Number(persons.value)
  const params = new URLSearchParams({
    tourId: String(tour.value.id),
    tourDate: tourDate.value,
    travelers: persons.value,
    total: String(total),
    experience: tour.value.name,
  })
  navigateTo(`/checkout?${params.toString()}`)
}

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const slug = route.params.slug

const { data: tour, pending, error } = useFetch(
  () => `${apiBase}/tours/${slug}`,
  {
    default: () => null
  }
)

const formatCategory = (cat: string | undefined) => {
  const cats: Record<string, string> = {
    adventure: 'Aventura',
    nature: 'Naturaleza',
    cultural: 'Cultural',
    water: 'Acuático',
    beach: 'Playa',
    wildlife: 'Fauna'
  }
  return cats[cat || ''] || cat || 'Tour'
}

const difficultyColor = computed(() => {
  const diff = tour.value?.difficulty
  if (diff === 'easy') return 'bg-green-100 text-green-700 border-green-200'
  if (diff === 'challenging') return 'bg-red-100 text-red-700 border-red-200'
  return 'bg-yellow-100 text-yellow-700 border-yellow-200'
})

const difficultyLabel = computed(() => {
  const diff = tour.value?.difficulty
  if (diff === 'easy') return 'Fácil'
  if (diff === 'challenging') return 'Exigente'
  return 'Moderado'
})

const getIncludes = () => {
  return [
    'Transporte ida y vuelta',
    'Guía profesional bilingüe',
    'Equipo de seguridad',
    'Snack y bebida',
    'Fotos del tour'
  ]
}

const getItinerary = () => {
  const duration = tour.value?.duration_hours || 3
  const startHour = 8
  const endHour = startHour + duration
  const formatHour = (h: number) => {
    const hours = Math.floor(h)
    const minutes = Math.round((h % 1) * 60)
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
  }
  return [
    { time: '08:00', activity: 'Recogida en hotel' },
    { time: '09:00', activity: 'Llegada e instrucciones' },
    { time: '09:30', activity: 'Inicio de la aventura' },
    { time: formatHour(endHour), activity: 'Fin del tour y regreso' }
  ]
}

const getWhatToBring = () => {
  return ['Zapatos cerrados', 'Ropa de cambio', 'Repelente', 'Gorra', 'Cámara']
}

useSeo({
  title: computed(() => tour.value?.name ? `${tour.value.name} | Costa Rica Travel` : 'Tour'),
  description: computed(() => tour.value?.description || ''),
  ogType: 'website'
})
</script>