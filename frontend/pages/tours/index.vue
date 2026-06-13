<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Hero Search -->
    <section class="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 text-white py-12">
      <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-3xl md:text-4xl font-bold mb-4">
            {{ $t('tours.title', 'Descubre Experiencias Únicas') }}
          </h1>
          <p class="text-white/80 text-lg mb-8">
            Encuentra y reserva los mejores tours en Costa Rica
          </p>

          <!-- Search Bar -->
          <div class="bg-white rounded-2xl shadow-elevated p-4">
            <div class="flex flex-col md:flex-row gap-3">
              <div class="flex-1 relative">
                <input
                  v-model="filters.query"
                  type="text"
                  placeholder="¿Qué experiencia buscas?"
                  class="w-full px-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-primary-500 text-gray-900"
                  @keyup.enter="searchTours"
                />
              </div>
              <div class="flex gap-2">
                <UiSelect
                  :model-value="filters.sortBy ?? ''"
                  :options="filterOptions.sortOptions"
                  placeholder="Ordenar"
                  @update:model-value="filters.sortBy = ($event as any) || undefined"
                />
                <button
                  @click="searchTours"
                  class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors flex items-center gap-2"
                >
                  <Search class="w-5 h-5" />
                  Buscar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Section -->
    <section class="py-8">
      <div class="container mx-auto px-4">
        <div class="flex gap-8">
          <!-- Filters Sidebar -->
          <SearchFilters
            :filters="filters"
            :filter-options="filterOptions"
            :active-filters-count="activeFiltersCount"
            :has-active-filters="hasActiveFilters"
            :loading="loading"
            @update:filters="updateFilters"
            @clear="clearFilters"
            @clear-filter="clearFilter"
          />

          <!-- Results Grid -->
          <div class="flex-1">
            <!-- Results Header -->
            <div class="flex items-center justify-between mb-6">
              <div class="text-gray-600">
                <span v-if="loading" class="flex items-center gap-2">
                  <Loader2 class="w-4 h-4 animate-spin" />
                  Buscando...
                </span>
                <span v-else>
                  <strong class="text-gray-900">{{ totalCount }}</strong> experiencias encontradas
                </span>
              </div>

              <!-- View Toggle (placeholder for map view) -->
              <div class="flex items-center gap-2 bg-white rounded-lg p-1 shadow-sm border border-gray-200">
                <button class="px-3 py-1.5 rounded-md bg-primary-50 text-primary-700 font-medium text-sm">
                  <Grid3X3 class="w-4 h-4" />
                </button>
                <button class="px-3 py-1.5 rounded-md text-gray-600 hover:bg-gray-50 font-medium text-sm">
                  <Map class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div v-for="n in 6" :key="n" class="bg-white rounded-2xl overflow-hidden shadow-sm">
                <div class="aspect-[4/3] bg-gray-200 animate-pulse" />
                <div class="p-5 space-y-3">
                  <div class="h-4 bg-gray-200 rounded w-3/4 animate-pulse" />
                  <div class="h-3 bg-gray-200 rounded w-full animate-pulse" />
                  <div class="h-3 bg-gray-200 rounded w-2/3 animate-pulse" />
                </div>
              </div>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="text-center py-12">
              <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle class="w-8 h-8 text-red-600" />
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Error al cargar tours</h3>
              <p class="text-gray-600 mb-4">{{ error }}</p>
              <button
                @click="searchTours"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Intentar de nuevo
              </button>
            </div>

            <!-- Empty State -->
            <div v-else-if="tours.length === 0" class="text-center py-12">
              <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <SearchX class="w-8 h-8 text-gray-400" />
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">No encontramos resultados</h3>
              <p class="text-gray-600 mb-4">Intenta ajustar tus filtros o términos de búsqueda</p>
              <button
                @click="clearFilters"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Limpiar filtros
              </button>
            </div>

            <!-- Results Grid -->
            <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <TourCard
                v-for="tour in tours"
                :key="tour.id"
                :tour="tour"
                @view="navigateToTour"
                @book="bookTour"
                @favorite="toggleFavorite"
              />
            </div>

            <!-- Pagination -->
            <Pagination
              v-if="totalCount > pageSize"
              :current-page="currentPage"
              :total-pages="Math.ceil(totalCount / pageSize)"
              :total-items="totalCount"
              :items-per-page="pageSize"
              @page-change="setPage"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  Search,
  Loader2,
  AlertCircle,
  SearchX,
  Grid3X3,
  Map
} from 'lucide-vue-next'
import Pagination from '~/components/ui/Pagination.vue'

const router = useRouter()

// Use search composable
const {
  tours,
  loading,
  error,
  filters,
  filterOptions,
  totalCount,
  currentPage,
  pageSize,
  activeFiltersCount,
  hasActiveFilters,
  searchTours,
  updateFilters,
  clearFilters,
  clearFilter,
  setPage,
  init
} = useSearch()

// SEO
useSeo({
  title: 'Tours y Experiencias en Costa Rica',
  description: 'Descubre y reserva tours en Costa Rica: aventura, naturaleza, cultura, playa. Encuentra la experiencia perfecta con filtros avanzados.',
  keywords: 'tours Costa Rica, excursiones, aventura, reservar tour, filtros búsqueda',
  ogType: 'website'
})

// Actions
const navigateToTour = (tourId: string) => {
  router.push(`/tours/${tourId}`)
}

const bookTour = (tourId: string) => {
  router.push(`/checkout?tour=${tourId}`)
}

const toggleFavorite = (tourId: string) => {
  // TODO: Implement wishlist functionality
}

// Initialize on mount
onMounted(() => {
  init()
})
</script>
