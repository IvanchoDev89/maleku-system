<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ $t('properties.title') }}</h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">Encuentra los mejores hoteles, resorts y alojamientos en Costa Rica</p>
      </div>

      <!-- Search Bar -->
      <div class="bg-white rounded-2xl shadow-lg p-4 mb-8 max-w-4xl mx-auto">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1 relative">
            <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar hoteles..."
              class="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-gray-900"
              @keyup.enter="performSearch"
            />
          </div>
          <button
            @click="performSearch"
            class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
          >
            <Search class="w-5 h-5" />
            <span>Buscar</span>
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-2 text-gray-700">Destino</label>
            <UiSelect v-model="filters.region" :options="regionOptions" placeholder="Todos" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2 text-gray-700">Tipo</label>
            <UiSelect v-model="filters.type" :options="typeOptions" placeholder="Todos" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2 text-gray-700">Precio máximo</label>
            <UiSelect v-model="filters.maxPrice" :options="priceOptions" placeholder="Cualquiera" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2 text-gray-700">Rating mínimo</label>
            <UiSelect v-model="filters.minRating" :options="ratingOptions" placeholder="Cualquiera" />
          </div>
        </div>
      </div>

      <!-- Results Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <p class="text-gray-700 font-medium">
          <span class="text-gray-900 font-bold">{{ totalItems }}</span> propiedades encontradas
        </p>
        <UiSelect v-model="filters.sort" :options="sortOptions" />
      </div>

      <!-- Loading -->
      <div v-if="pending" class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="i in 6" :key="i" class="bg-white rounded-xl overflow-hidden shadow-sm">
          <div class="h-52 bg-gray-200 animate-pulse"></div>
          <div class="p-6 space-y-3">
            <div class="h-6 bg-gray-200 rounded w-3/4 animate-pulse"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
            <div class="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-16">
        <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertCircle class="w-12 h-12 text-red-400" />
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Error al cargar propiedades</h3>
        <p class="text-gray-600 mb-6">Por favor intenta de nuevo más tarde.</p>
        <button @click="refreshPage" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors">
          Reintentar
        </button>
      </div>

      <!-- Properties Grid -->
      <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <NuxtLink
          v-for="property in properties"
          :key="property.id"
          :to="`/hoteles/${property.slug}`"
          class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 group"
        >
          <div class="relative h-52 overflow-hidden">
            <NuxtImg
              :src="property.cover_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945'"
              :alt="property.name"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              width="800"
              height="400"
              format="webp"
              loading="lazy"
            />
            <span class="absolute top-4 left-4 px-3 py-1 bg-primary-600 text-white text-xs font-bold rounded-full">
              {{ formatPropertyType(property.property_type) }}
            </span>
          </div>
          <div class="p-6">
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1">
                <h3 class="font-bold text-gray-900 text-lg group-hover:text-primary-600 transition-colors">{{ property.name }}</h3>
                <p class="text-gray-500 text-sm mt-1 flex items-center gap-1">
                  <MapPin class="w-3 h-3" />
                  {{ property.city }}, {{ property.region }}
                </p>
              </div>
              <div class="flex items-center gap-1 bg-amber-50 px-2 py-1 rounded-lg">
                <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                <span class="font-bold text-gray-900">{{ (property.rating ?? 0).toFixed(1) }}</span>
              </div>
            </div>
            <p class="mt-3 text-gray-600 text-sm line-clamp-2">{{ property.short_description }}</p>
            <div class="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
              <div>
                <span class="text-2xl font-bold text-primary-600">${{ property.base_price }}</span>
                <span class="text-gray-500 text-sm">/noche</span>
              </div>
              <span class="text-gray-500 text-sm">{{ property.total_reviews }} reseñas</span>
            </div>
          </div>
        </NuxtLink>
      </div>

      <!-- Pagination -->
      <Pagination
        v-if="!pending && !error && totalItems > 0"
        :current-page="currentPage"
        :total-pages="totalPages"
        :total-items="totalItems"
        :items-per-page="pageSize"
        @page-change="handlePageChange"
      />

      <!-- Empty State -->
      <div v-if="!pending && !error && properties.length === 0" class="text-center py-16">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <Building2 class="w-12 h-12 text-gray-400" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">No hay hoteles disponibles</h2>
        <p class="text-gray-600 mb-6">Intenta con otros filtros de búsqueda</p>
        <button @click="clearFilters" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700">
          Limpiar filtros
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Search, MapPin, Star, Building2 } from 'lucide-vue-next'
import Pagination from '~/components/ui/Pagination.vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 12

const filters = reactive({
  region: '',
  type: '',
  maxPrice: '',
  minRating: '',
  sort: 'rating'
})

const getQueryParams = () => {
  const params = new URLSearchParams()
  params.set('page', currentPage.value.toString())
  params.set('page_size', pageSize.toString())
  if (filters.region) params.set('region', filters.region)
  if (filters.type) params.set('property_type', filters.type)
  if (filters.maxPrice) params.set('max_price', filters.maxPrice)
  if (filters.minRating) params.set('min_rating', filters.minRating)
  if (filters.sort) params.set('sort', filters.sort)
  return params.toString()
}

const { data: apiData, pending, error, refresh } = useFetch(
  () => `${apiBase}/properties?${getQueryParams()}`,
  {
    key: 'hoteles-list',
    default: () => ({ items: [], total: 0, page: 1, total_pages: 1 })
  }
)

const properties = computed(() => apiData.value?.items || [])
const totalItems = computed(() => apiData.value?.total || 0)
const totalPages = computed(() => apiData.value?.total_pages || 1)

const regions = computed(() => {
  const unique = new Set(properties.value.map((p: any) => p.region).filter(Boolean))
  return Array.from(unique).sort()
})

const regionOptions = computed(() => [
  { value: '', label: 'Todos' },
  ...regions.value.map((r: string) => ({ value: r, label: r })),
])

const typeOptions = [
  { value: '', label: 'Todos' },
  { value: 'hotel', label: 'Hotel' },
  { value: 'resort', label: 'Resort' },
  { value: 'villa', label: 'Villa' },
  { value: 'boutique', label: 'Boutique' },
  { value: 'eco_lodge', label: 'Eco Lodge' },
]

const priceOptions = [
  { value: '', label: 'Cualquiera' },
  { value: '100', label: 'Hasta $100' },
  { value: '200', label: 'Hasta $200' },
  { value: '300', label: 'Hasta $300' },
  { value: '500', label: 'Hasta $500' },
]

const ratingOptions = [
  { value: '', label: 'Cualquiera' },
  { value: '4.5', label: '4.5+ ⭐' },
  { value: '4.0', label: '4.0+ ⭐' },
]

const sortOptions = [
  { value: 'rating', label: 'Mejor valorados' },
  { value: 'price_asc', label: 'Precio: menor a mayor' },
  { value: 'price_desc', label: 'Precio: mayor a menor' },
]

const formatPropertyType = (type: string) => {
  const types: Record<string, string> = {
    hotel: 'Hotel',
    resort: 'Resort',
    villa: 'Villa',
    boutique: 'Boutique',
    eco_lodge: 'Eco Lodge'
  }
  return types[type] || type || 'Hotel'
}

const performSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
  }
}

const clearFilters = () => {
  filters.region = ''
  filters.type = ''
  filters.maxPrice = ''
  filters.minRating = ''
  filters.sort = 'rating'
  currentPage.value = 1
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const refreshPage = () => {
  currentPage.value = 1
  refresh()
}

watch(filters, () => {
  currentPage.value = 1
}, { deep: true })

useSeo({
  title: 'Hoteles en Costa Rica',
  description: 'Encuentra los mejores hoteles, resorts y alojamientos en Costa Rica. Reserva tu hospedaje en Guanacaste, Arenal, Monteverde, Manuel Antonio y más.',
  keywords: 'hoteles Costa Rica, resorts, alojamiento, booking, Guanacaste, Arenal, Monteverde, Manuel Antonio, villa, eco lodge',
  ogType: 'website'
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
