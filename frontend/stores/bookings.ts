import { defineStore } from 'pinia'
import type { Booking, BookingStats, PaginationControls } from '~/types'

interface BookingsState {
  items: Booking[]
  current: Booking | null
  stats: BookingStats | null
  loading: boolean
  error: string | null
  pagination: PaginationControls
}

export const useBookingsStore = defineStore('bookings', {
  state: (): BookingsState => ({
    items: [],
    current: null,
    stats: null,
    loading: false,
    error: null,
    pagination: {
      currentPage: 1,
      totalPages: 1,
      hasNext: false,
      hasPrev: false,
      totalItems: 0,
      itemsPerPage: 10
    }
  }),

  getters: {
    activeBookings: (state) => state.items.filter(b => b.status === 'confirmed' || b.status === 'pending'),
    completedBookings: (state) => state.items.filter(b => b.status === 'completed')
  },

  actions: {
    async fetchAll(params?: Record<string, any>) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        const response = await api.get<{ items: Booking[]; total: number; page: number; total_pages: number }>('/bookings', { page: this.pagination.currentPage, ...params })
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
        this.error = e?.data?.detail || 'Error al cargar reservas'
      } finally {
        this.loading = false
      }
    },

    async fetchById(id: string) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        this.current = await api.get<Booking>(`/bookings/${id}`)
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar reserva'
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      const api = useApi()
      try {
        this.stats = await api.get<BookingStats>('/bookings/stats')
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar estadísticas'
      }
    },

    async create(bookingData: Partial<Booking>): Promise<Booking | null> {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        const created = await api.post<Booking>('/bookings', bookingData)
        this.items.unshift(created)
        return created
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al crear reserva'
        return null
      } finally {
        this.loading = false
      }
    },

    async cancel(id: string) {
      const api = useApi()
      try {
        const updated = await api.patch<Booking>(`/bookings/${id}/cancel`)
        const idx = this.items.findIndex(b => b.id === id)
        if (idx !== -1) this.items[idx] = updated
        if (this.current?.id === id) this.current = updated
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cancelar reserva'
      }
    },

    setPage(page: number) {
      this.pagination.currentPage = page
      this.fetchAll()
    }
  }
})
