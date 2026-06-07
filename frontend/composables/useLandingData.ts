/**
 * Composable para cargar datos dinámicos en la landing page
 * Conecta con el backend para tours, destinos y newsletter
 * REFACTOR: Usa useApi, useAsyncAction y tipos centralizados
 */
import type { Tour, Destination, NewsletterResponse } from '~/types'

export function useLandingData() {
  const api = useApi()
  const { pending, error, execute } = useAsyncAction({ defaultValue: [] })

  /**
   * Fetch featured tours from backend
   */
  async function fetchFeaturedTours(limit: number = 3): Promise<Tour[]> {
    return execute(
      async () => {
        const data = await api.get<{ items: Tour[] }>(`/tours?featured=true&page_size=${limit}`)
        return data.items || []
      },
      { defaultValue: [] }
    ) as Promise<Tour[]>
  }

  /**
   * Fetch destinations from backend
   */
  async function fetchDestinations(limit: number = 6): Promise<Destination[]> {
    return execute(
      async () => {
        const data = await api.get<Destination[]>('/destinations')
        return data.slice(0, limit)
      },
      { defaultValue: [] }
    ) as Promise<Destination[]>
  }

  /**
   * Subscribe to newsletter
   */
  async function subscribeNewsletter(email: string, firstName?: string): Promise<NewsletterResponse> {
    return execute(
      async () => {
        return await api.post<NewsletterResponse>('/newsletter/subscribe', {
          email,
          first_name: firstName
        })
      },
      { 
        defaultValue: { success: false, message: 'Error al suscribirse' }
      }
    ) as Promise<NewsletterResponse>
  }

  return {
    pending,
    error,
    fetchFeaturedTours,
    fetchDestinations,
    subscribeNewsletter
  }
}
