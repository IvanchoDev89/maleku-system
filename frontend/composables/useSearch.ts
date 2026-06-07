import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Tour, SearchFilters, TourSearchResponse } from '~/types'
import { TOUR_CATEGORIES, PAGINATION, SEARCH_FILTERS } from '~/config/constants'

export type { Tour, SearchFilters }

export function useSearch() {
  const route = useRoute()
  const router = useRouter()
  const api = useApi()
  
  // State
  const tours = ref<Tour[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(PAGINATION.searchPageSize)
  
  // Filtros desde URL o defaults
  const filters = ref<SearchFilters>({
    query: route.query.q as string || '',
    destination: route.query.destination as string || '',
    category: route.query.category as string || '',
    difficulty: route.query.difficulty as string || '',
    minPrice: route.query.minPrice ? parseInt(route.query.minPrice as string) : undefined,
    maxPrice: route.query.maxPrice ? parseInt(route.query.maxPrice as string) : undefined,
    minDuration: route.query.minDuration ? parseInt(route.query.minDuration as string) : undefined,
    maxDuration: route.query.maxDuration ? parseInt(route.query.maxDuration as string) : undefined,
    rating: route.query.rating ? parseInt(route.query.rating as string) : undefined,
    date: route.query.date as string || '',
    travelers: route.query.travelers ? parseInt(route.query.travelers as string) : 2,
    sortBy: (route.query.sortBy as SearchFilters['sortBy']) || 'popular'
  })
  
  // Opciones de filtros disponibles - using centralized constants
  const filterOptions = computed(() => ({
    categories: TOUR_CATEGORIES.map((cat: typeof TOUR_CATEGORIES[number]) => ({
      value: cat.value,
      label: cat.key, // i18n key, actual label resolved in component
      icon: cat.icon
    })),
    difficulties: SEARCH_FILTERS.difficulties,
    priceRanges: SEARCH_FILTERS.priceRanges,
    durations: SEARCH_FILTERS.durations,
    sortOptions: SEARCH_FILTERS.sortOptions,
    regions: SEARCH_FILTERS.regions
  }))
  
  // Computed
  const activeFiltersCount = computed(() => {
    let count = 0
    if (filters.value.category) count++
    if (filters.value.difficulty) count++
    if (filters.value.destination) count++
    if (filters.value.minPrice || filters.value.maxPrice) count++
    if (filters.value.minDuration || filters.value.maxDuration) count++
    if (filters.value.rating) count++
    if (filters.value.date) count++
    return count
  })
  
  const hasActiveFilters = computed(() => activeFiltersCount.value > 0)
  
  // Methods
  async function searchTours() {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams()
      
      if (filters.value.query) params.set('q', filters.value.query)
      if (filters.value.destination) params.set('destination', filters.value.destination)
      if (filters.value.category) params.set('category', filters.value.category)
      if (filters.value.difficulty) params.set('difficulty', filters.value.difficulty)
      if (filters.value.minPrice) params.set('min_price', filters.value.minPrice.toString())
      if (filters.value.maxPrice) params.set('max_price', filters.value.maxPrice.toString())
      if (filters.value.minDuration) params.set('min_duration', filters.value.minDuration.toString())
      if (filters.value.maxDuration) params.set('max_duration', filters.value.maxDuration.toString())
      if (filters.value.rating) params.set('min_rating', filters.value.rating.toString())
      if (filters.value.sortBy) params.set('sort', filters.value.sortBy)
      
      params.set('page', currentPage.value.toString())
      params.set('page_size', pageSize.value.toString())
      
      const data = await api.get<TourSearchResponse>(`/tours?${params.toString()}`)
      tours.value = data.items || []
      totalCount.value = data.total || 0
      
    } catch (err: any) {
      error.value = err?.message || err?.data?.detail || 'Error en búsqueda'
      console.error('Search error:', err)
    } finally {
      loading.value = false
    }
  }
  
  function updateFilters(newFilters: Partial<SearchFilters>) {
    filters.value = { ...filters.value, ...newFilters }
    currentPage.value = 1 // Reset page on filter change
    syncUrlWithFilters()
    searchTours()
  }
  
  function clearFilters() {
    filters.value = {
      query: '',
      destination: '',
      category: '',
      difficulty: '',
      sortBy: 'popular'
    }
    currentPage.value = 1
    syncUrlWithFilters()
    searchTours()
  }
  
  function clearFilter(key: keyof SearchFilters) {
    filters.value[key] = undefined
    syncUrlWithFilters()
    searchTours()
  }
  
  function syncUrlWithFilters() {
    const query: Record<string, string> = {}
    
    if (filters.value.query) query.q = filters.value.query
    if (filters.value.destination) query.destination = filters.value.destination
    if (filters.value.category) query.category = filters.value.category
    if (filters.value.difficulty) query.difficulty = filters.value.difficulty
    if (filters.value.minPrice) query.minPrice = filters.value.minPrice.toString()
    if (filters.value.maxPrice) query.maxPrice = filters.value.maxPrice.toString()
    if (filters.value.minDuration) query.minDuration = filters.value.minDuration.toString()
    if (filters.value.maxDuration) query.maxDuration = filters.value.maxDuration.toString()
    if (filters.value.rating) query.rating = filters.value.rating.toString()
    if (filters.value.date) query.date = filters.value.date
    if (filters.value.travelers) query.travelers = filters.value.travelers.toString()
    if (filters.value.sortBy && filters.value.sortBy !== 'popular') query.sortBy = filters.value.sortBy
    if (currentPage.value > 1) query.page = currentPage.value.toString()
    
    router.replace({ query })
  }
  
  function setPage(page: number) {
    currentPage.value = page
    syncUrlWithFilters()
    searchTours()
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  
  // Watch for URL changes (browser back/forward)
  watch(() => route.query, (newQuery) => {
    filters.value = {
      query: newQuery.q as string || '',
      destination: newQuery.destination as string || '',
      category: newQuery.category as string || '',
      difficulty: newQuery.difficulty as string || '',
      minPrice: newQuery.minPrice ? parseInt(newQuery.minPrice as string) : undefined,
      maxPrice: newQuery.maxPrice ? parseInt(newQuery.maxPrice as string) : undefined,
      minDuration: newQuery.minDuration ? parseInt(newQuery.minDuration as string) : undefined,
      maxDuration: newQuery.maxDuration ? parseInt(newQuery.maxDuration as string) : undefined,
      rating: newQuery.rating ? parseInt(newQuery.rating as string) : undefined,
      date: newQuery.date as string || '',
      travelers: newQuery.travelers ? parseInt(newQuery.travelers as string) : 2,
      sortBy: (newQuery.sortBy as SearchFilters['sortBy']) || 'popular'
    }
    currentPage.value = newQuery.page ? parseInt(newQuery.page as string) : 1
    searchTours()
  }, { deep: true })
  
  // Initial search
  const init = () => {
    searchTours()
  }
  
  return {
    // State
    tours,
    loading,
    error,
    filters,
    totalCount,
    currentPage,
    pageSize,
    
    // Computed
    filterOptions,
    activeFiltersCount,
    hasActiveFilters,
    
    // Methods
    searchTours,
    updateFilters,
    clearFilters,
    clearFilter,
    setPage,
    init
  }
}
