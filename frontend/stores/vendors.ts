import { defineStore } from 'pinia'
import type { Vendor, VendorAnalytics } from '~/types'

interface VendorsState {
  items: Vendor[]
  current: Vendor | null
  analytics: VendorAnalytics | null
  loading: boolean
  error: string | null
}

export const useVendorsStore = defineStore('vendors', {
  state: (): VendorsState => ({
    items: [],
    current: null,
    analytics: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchAll(params?: Record<string, any>) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        this.items = await api.get<Vendor[]>('/vendors', params)
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar vendors'
      } finally {
        this.loading = false
      }
    },

    async fetchById(id: string) {
      const api = useApi()
      this.loading = true
      this.error = null
      try {
        this.current = await api.get<Vendor>(`/vendors/${id}`)
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar vendor'
      } finally {
        this.loading = false
      }
    },

    async fetchAnalytics(id?: string) {
      const api = useApi()
      try {
        const endpoint = id ? `/vendors/${id}/analytics` : '/vendors/analytics'
        this.analytics = await api.get<VendorAnalytics>(endpoint)
      } catch (e: any) {
        this.error = e?.data?.detail || 'Error al cargar analytics'
      }
    }
  }
})
