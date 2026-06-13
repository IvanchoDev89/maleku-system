import { defineStore } from 'pinia'
import type { SearchResult, Tour, SearchFilters } from '~/types'

interface SearchState {
  query: string
  results: SearchResult | null
  tours: Tour[]
  loading: boolean
  error: string | null
  filters: SearchFilters
}

export const useSearchStore = defineStore('search', {
  state: (): SearchState => ({
    query: '',
    results: null,
    tours: [],
    loading: false,
    error: null,
    filters: {}
  }),

  actions: {
    async search(query: string) {
      const api = useApi()
      this.query = query
      this.loading = true
      this.error = null
      try {
        this.results = await api.get<SearchResult>('/search', { q: query, ...this.filters })
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al buscar'
      } finally {
        this.loading = false
      }
    },

    async searchTours(params?: Record<string, any>) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        const response = await api.get<{ items: Tour[] }>('/tours', { ...this.filters, ...params })
        this.tours = response.items
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al buscar tours'
      } finally {
        this.loading = false
      }
    },

    setFilters(filters: SearchFilters) {
      this.filters = filters
    },

    clearResults() {
      this.results = null
      this.query = ''
      this.tours = []
      this.filters = {}
    }
  }
})
