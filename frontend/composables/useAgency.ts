import { ref } from 'vue'
import type { AgencyLandingData } from '~/types'

export const useAgency = () => {
  const api = useApi()

  const landing = ref<AgencyLandingData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const getLandingData = async (slug: string): Promise<AgencyLandingData | null> => {
    loading.value = true
    error.value = null
    try {
      const data = await api.get<AgencyLandingData>(`/vendors/slug/${slug}/landing`)
      landing.value = data
      return data
    } catch (e: any) {
      error.value = e?.data?.detail || e?.message || 'Error loading agency data'
      return null
    } finally {
      loading.value = false
    }
  }

  const submittingReview = ref(false)
  const reviewSubmitted = ref(false)
  const reviewError = ref<string | null>(null)

  const submitReview = async (bookingId: string, rating: number, title: string | null, comment: string | null): Promise<boolean> => {
    submittingReview.value = true
    reviewError.value = null
    reviewSubmitted.value = false
    try {
      await api.post('/reviews', { booking_id: bookingId, rating, title, comment })
      reviewSubmitted.value = true
      return true
    } catch (e: any) {
      reviewError.value = e?.data?.detail || e?.message || 'Error submitting review'
      return false
    } finally {
      submittingReview.value = false
    }
  }

  const clear = () => {
    landing.value = null
    error.value = null
  }

  return {
    landing,
    loading,
    error,
    getLandingData,
    submitReview,
    submittingReview,
    reviewSubmitted,
    reviewError,
    clear,
  }
}
