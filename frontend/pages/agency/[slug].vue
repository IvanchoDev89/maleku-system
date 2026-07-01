<template>
  <div class="min-h-screen bg-gray-50">
    <div v-if="loading" class="max-w-6xl mx-auto px-4 py-12">
      <div class="animate-pulse space-y-6">
        <div class="h-64 bg-gray-200 rounded-2xl" />
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <div class="h-48 bg-gray-200 rounded-2xl" />
            <div class="h-64 bg-gray-200 rounded-2xl" />
          </div>
          <div class="space-y-6">
            <div class="h-48 bg-gray-200 rounded-2xl" />
            <div class="h-48 bg-gray-200 rounded-2xl" />
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="max-w-4xl mx-auto px-4 py-20 text-center">
      <Icon name="lucide:building-2" class="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Agencia no encontrada</h1>
      <p class="text-gray-500 mb-6">{{ error }}</p>
      <NuxtLink to="/" class="text-primary-600 hover:text-primary-700 font-medium hover:underline">
        Volver al inicio
      </NuxtLink>
    </div>

    <div v-else-if="landingData" class="max-w-6xl mx-auto px-4 py-8 space-y-8">
      <AgencyHero :vendor="landingData" />

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2 space-y-8">
          <AgencyAbout :vendor="landingData" />
          <AgencyServices
            :properties="landingData.properties"
            :properties_has_more="landingData.properties_has_more"
            :tours="landingData.tours"
            :tours_has_more="landingData.tours_has_more"
            :vehicles="landingData.vehicles"
            :vehicles_has_more="landingData.vehicles_has_more"
            :boats="landingData.boats"
            :boats_has_more="landingData.boats_has_more"
            :transportation="landingData.transportation"
            :transportation_has_more="landingData.transportation_has_more"
            :stats="landingData.stats"
            @view-all="handleViewAll"
          />
          <AgencyReviews
            :reviews="landingData.reviews"
            :total="landingData.reviews_total"
            :average-rating="landingData.reviews_average_rating"
          />
          <ReviewForm
            v-if="landingData.can_review && landingData.eligible_booking_ids.length > 0"
            :booking-id="landingData.eligible_booking_ids[0]"
            @submitted="onReviewSubmitted"
          />
        </div>

        <div class="space-y-6">
          <AgencyRanking :ranking="landingData.ranking" :rating="landingData.rating || 0" />

          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-semibold text-gray-900 mb-4 text-sm uppercase tracking-wider text-gray-500">Estadísticas</h3>
            <div class="space-y-3">
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Miembro desde</span>
                <span class="font-medium text-gray-900">{{ formatMemberSince(landingData.stats.member_since) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Reservas completadas</span>
                <span class="font-medium text-gray-900">{{ landingData.stats.total_bookings }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Servicios totales</span>
                <span class="font-medium text-gray-900">{{ totalServices }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">Opiniones</span>
                <span class="font-medium text-gray-900">{{ landingData.stats.total_reviews }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const route = useRoute()
const agency = useAgency()

const slug = computed(() => route.params.slug as string)
const loading = computed(() => agency.loading.value)
const error = computed(() => agency.error.value)
const landingData = computed(() => agency.landing.value)

const totalServices = computed(() => {
  if (!agency.landing.value) return 0
  const s = agency.landing.value.stats
  return s.total_properties + s.total_tours + s.total_vehicles + s.total_boats + s.total_transportation
})

const formatMemberSince = (date: string | null) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'long',
  })
}

const handleViewAll = (type: string) => {
  // Future: navigate to filtered search page
}

const onReviewSubmitted = () => {
  if (agency.landing.value) {
    agency.landing.value.can_review = false
  }
}

onMounted(async () => {
  if (slug.value) {
    await agency.getLandingData(slug.value)
  }
})
</script>
