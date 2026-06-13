import { defineStore } from 'pinia'
import type { Property, SearchFilters, PaginationControls } from '~/types'

interface PropertiesState {
  items: Property[]
  current: Property | null
  loading: boolean
  error: string | null
  pagination: PaginationControls
  filters: SearchFilters
}

export const usePropertiesStore = defineStore('properties', {
  state: (): PropertiesState => ({
    items: [],
    current: null,
    loading: false,
    error: null,
    pagination: {
      currentPage: 1,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
      totalItems: 0,
      itemsPerPage: 12
    },
    filters: {}
  }),

  getters: {
    featured: (state) => state.items.filter(p => p.rating && p.rating >= 4.5).slice(0, 6),
    byRegion: (state) => {
      const groups: Record<string, Property[]> = {}
      for (const p of state.items) {
        if (!groups[p.region]) groups[p.region] = []
        groups[p.region].push(p)
      }
      return groups
    }
  },

  actions: {
    async fetchAll(params?: Record<string, any>) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        const response = await api.get<{ items: Property[]; total: number; page: number; total_pages: number }>('/properties', { ...this.filters, ...params })
        this.items = response.items
        this.pagination = {
          currentPage: response.page,
          totalPages: response.total_pages,
          hasNext: response.page < response.total_pages,
          hasPrev: response.page > 1,
          totalItems: response.total,
          itemsPerPage: this.pagination.itemsPerPage
        }
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar propiedades'
      } finally {
        this.loading = false
      }
    },

    async fetchById(id: string) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        this.current = await api.get<Property>(`/properties/${id}`)
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar propiedad'
      } finally {
        this.loading = false
      }
    },

    setFilters(filters: SearchFilters) {
      this.filters = filters
      this.pagination.currentPage = 1
    },

    setPage(page: number) {
      this.pagination.currentPage = page
      this.fetchAll({ page })
    }
  }
})
