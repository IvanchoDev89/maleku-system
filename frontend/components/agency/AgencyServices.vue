<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
    <h2 class="text-xl font-bold text-gray-900 mb-6">Servicios</h2>

    <div v-if="!hasServices" class="text-center py-8 text-gray-400">
      <Icon name="lucide:package" class="w-12 h-12 mx-auto mb-3 text-gray-300" />
      <p>No hay servicios disponibles</p>
    </div>

    <div v-for="(group, idx) in serviceGroups" :key="group.type" v-else>
      <div v-if="group.items.length > 0" :class="{ 'mt-8': idx > 0 }">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Icon :name="group.icon" class="w-5 h-5 text-primary-500" />
            {{ group.label }}
          </h3>
          <span class="text-sm text-gray-400">{{ group.items.length }} {{ group.items.length === 1 ? 'disponible' : 'disponibles' }}</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <NuxtLink
            v-for="item in group.items"
            :key="item.id"
            :to="group.linkTo(item)"
            class="group bg-gray-50 rounded-xl overflow-hidden border border-gray-100 hover:shadow-md hover:border-primary-200 transition-all duration-200"
          >
            <div class="aspect-[16/10] bg-gray-200 relative overflow-hidden">
              <img
                v-if="item.cover_image"
                :src="item.cover_image"
                :alt="item.name"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <Icon :name="group.icon" class="w-10 h-10 text-gray-300" />
              </div>
              <div v-if="item.price > 0" class="absolute top-2 right-2 bg-white/90 backdrop-blur-sm rounded-lg px-2.5 py-1 text-sm font-bold text-gray-900 shadow-sm">
                ${{ formatPrice(item.price, group.priceLabel) }}
              </div>
            </div>
            <div class="p-3">
              <p class="font-semibold text-gray-900 text-sm truncate group-hover:text-primary-600 transition-colors">
                {{ item.name || `${item.brand || ''} ${item.model || ''}` }}
              </p>
              <div class="flex items-center gap-2 mt-1.5 text-xs text-gray-500">
                <StarRating v-if="item.rating" :rating="item.rating" size="sm" />
                <span v-if="item.city || item.location">{{ item.city || item.location }}</span>
                <span v-if="item.duration_hours">{{ item.duration_hours }}h</span>
              </div>
            </div>
          </NuxtLink>
        </div>
        <button
          v-if="group.hasMore"
          @click="$emit('view-all', group.type)"
          class="mt-3 text-sm text-primary-600 hover:text-primary-700 font-medium hover:underline"
        >
          Ver todos ({{ group.totalCount }}+)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgencyLandingService } from '~/types'

const props = defineProps<{
  properties: AgencyLandingService[]
  properties_has_more: boolean
  tours: AgencyLandingService[]
  tours_has_more: boolean
  vehicles: AgencyLandingService[]
  vehicles_has_more: boolean
  boats: AgencyLandingService[]
  boats_has_more: boolean
  transportation: AgencyLandingService[]
  transportation_has_more: boolean
  stats: {
    total_properties: number
    total_tours: number
    total_vehicles: number
    total_boats: number
    total_transportation: number
  }
}>()

defineEmits<{
  'view-all': [type: string]
}>()

const formatPrice = (price: number, label: string) => {
  return `${price.toLocaleString()}${label}`
}

interface ServiceGroup {
  type: string
  label: string
  icon: string
  items: AgencyLandingService[]
  hasMore: boolean
  totalCount: number
  priceLabel: string
  linkTo: (item: AgencyLandingService) => string
}

const serviceGroups = computed<ServiceGroup[]>(() => {
  const groups: ServiceGroup[] = [
    {
      type: 'property',
      label: 'Hoteles & Propiedades',
      icon: 'lucide:building-2',
      items: props.properties,
      hasMore: props.properties_has_more,
      totalCount: props.stats.total_properties,
      priceLabel: '/noche',
      linkTo: (item) => `/hoteles/${item.slug}`,
    },
    {
      type: 'tour',
      label: 'Tours & Experiencias',
      icon: 'lucide:mountain',
      items: props.tours,
      hasMore: props.tours_has_more,
      totalCount: props.stats.total_tours,
      priceLabel: '',
      linkTo: (item) => `/tours/${item.slug}`,
    },
    {
      type: 'vehicle',
      label: 'Renta de Autos',
      icon: 'lucide:car',
      items: props.vehicles,
      hasMore: props.vehicles_has_more,
      totalCount: props.stats.total_vehicles,
      priceLabel: '/día',
      linkTo: () => '#',
    },
    {
      type: 'boat',
      label: 'Equipo Náutico',
      icon: 'lucide:ship',
      items: props.boats,
      hasMore: props.boats_has_more,
      totalCount: props.stats.total_boats,
      priceLabel: '/día',
      linkTo: () => '#',
    },
    {
      type: 'transportation',
      label: 'Transporte Privado',
      icon: 'lucide:bus',
      items: props.transportation,
      hasMore: props.transportation_has_more,
      totalCount: props.stats.total_transportation,
      priceLabel: '',
      linkTo: () => '#',
    },
  ]
  return groups
})

const hasServices = computed(() => {
  return serviceGroups.value.some(g => g.items.length > 0)
})
</script>
