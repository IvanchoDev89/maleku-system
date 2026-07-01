<template>
  <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800">
    <div v-if="vendor.cover_image" class="absolute inset-0">
      <img :src="vendor.cover_image" :alt="vendor.business_name" class="w-full h-full object-cover opacity-30" />
    </div>
    <div class="relative z-10 px-8 py-16 sm:px-12 sm:py-20 flex flex-col sm:flex-row items-center gap-8">
      <div v-if="vendor.logo_url" class="shrink-0">
        <img :src="vendor.logo_url" :alt="vendor.business_name"
          class="w-24 h-24 sm:w-32 sm:h-32 rounded-2xl border-4 border-white/30 shadow-xl object-cover" />
      </div>
      <div v-else class="shrink-0 w-24 h-24 sm:w-32 sm:h-32 rounded-2xl bg-white/20 flex items-center justify-center border-4 border-white/30">
        <Icon name="lucide:building-2" class="w-12 h-12 text-white/60" />
      </div>
      <div class="text-center sm:text-left">
        <div class="flex items-center gap-3 justify-center sm:justify-start mb-2">
          <h1 class="text-3xl sm:text-4xl font-bold text-white">{{ vendor.business_name }}</h1>
          <span v-if="vendor.is_verified"
            class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-500/30 text-blue-200 text-xs font-medium border border-blue-400/30">
            <Icon name="lucide:badge-check" class="w-3.5 h-3.5" />
            Verificada
          </span>
        </div>
        <p class="text-primary-100 text-lg mb-4">{{ businessTypeLabel }}</p>
        <div class="flex items-center gap-4 justify-center sm:justify-start">
          <StarRating :rating="vendor.rating || 0" size="md" show-value />
          <span class="text-primary-200 text-sm">
            ({{ vendor.total_reviews }} {{ vendor.total_reviews === 1 ? 'opinión' : 'opiniones' }})
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  vendor: {
    business_name: string
    business_type: string
    description: string | null
    logo_url: string | null
    cover_image: string | null
    rating: number | null
    total_reviews: number
    is_verified: boolean
  }
}>()

const businessTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    hotel: 'Hotel & Alojamiento',
    tour_operator: 'Tour Operador',
    transportation: 'Transporte',
    travel_agency: 'Agencia de Viajes',
    rental: 'Renta de Autos',
    boat: 'Equipo Náutico',
  }
  return labels[props.vendor.business_type] || props.vendor.business_type
})
</script>
