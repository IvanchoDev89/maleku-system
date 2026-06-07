<script setup lang="ts">
/**
 * TourCard - Tarjeta de tour para resultados de búsqueda
 * Con badges, rating, precio y acciones rápidas
 */
import { computed } from 'vue'
import { 
  Clock, 
  Star, 
  MapPin, 
  Users, 
  Zap,
  ChevronRight,
  Heart
} from 'lucide-vue-next'
import type { Tour } from '~/composables/useSearch'

const props = defineProps<{
  tour: Tour
  featured?: boolean
}>()

const emit = defineEmits<{
  'view': [tourId: string]
  'book': [tourId: string]
  'favorite': [tourId: string]
}>()

const difficultyConfig = {
  easy: { label: 'Fácil', color: 'bg-green-100 text-green-700 border-green-200' },
  medium: { label: 'Moderado', color: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
  hard: { label: 'Exigente', color: 'bg-red-100 text-red-700 border-red-200' }
}

const categoryIcons: Record<string, string> = {
  adventure: '🏔️',
  nature: '🌿',
  wildlife: '🦥',
  beach: '🏖️',
  culture: '🏛️',
  wellness: '🧘'
}

const difficulty = computed(() => {
  return difficultyConfig[props.tour.difficulty] || difficultyConfig.easy
})

const discount = computed(() => {
  if (!props.tour.original_price || props.tour.original_price <= props.tour.price) return null
  return Math.round(((props.tour.original_price - props.tour.price) / props.tour.original_price) * 100)
})

const formatDuration = (duration: string) => {
  return duration.replace('hours', 'h').replace('hour', 'h')
}
</script>

<template>
  <article 
    class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100"
    :class="{ 'ring-2 ring-primary-500 ring-offset-2': featured }"
  >
    <!-- Image Container -->
    <div class="relative aspect-[4/3] overflow-hidden">
      <NuxtImg
        :src="tour.image_url || '/images/placeholder-tour.jpg'"
        :alt="tour.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        loading="lazy"
        width="400"
        height="300"
        format="webp"
      />
      
      <!-- Badges -->
      <div class="absolute top-3 left-3 flex flex-wrap gap-2">
        <!-- Category Badge -->
        <span 
          class="px-2.5 py-1 bg-white/95 backdrop-blur-sm rounded-full text-sm font-medium shadow-sm"
        >
          {{ categoryIcons[tour.category] || '🎯' }} {{ tour.category }}
        </span>
        
        <!-- Featured Badge -->
        <span 
          v-if="tour.is_featured"
          class="px-2.5 py-1 bg-accent-500 text-white rounded-full text-xs font-bold shadow-sm flex items-center gap-1"
        >
          <Zap class="w-3 h-3" />
          Destacado
        </span>
        
        <!-- Discount Badge -->
        <span 
          v-if="discount"
          class="px-2.5 py-1 bg-red-500 text-white rounded-full text-xs font-bold shadow-sm"
        >
          -{{ discount }}%
        </span>
      </div>
      
      <!-- Favorite Button -->
      <button
        @click.prevent="emit('favorite', tour.id)"
        class="absolute top-3 right-3 w-9 h-9 bg-white/95 backdrop-blur-sm rounded-full flex items-center justify-center shadow-sm hover:bg-white transition-colors"
      >
        <Heart class="w-4 h-4 text-gray-600 hover:text-red-500 transition-colors" />
      </button>
      
      <!-- Difficulty Badge (bottom) -->
      <div class="absolute bottom-3 left-3">
        <span 
          class="px-2.5 py-1 rounded-full text-xs font-semibold border"
          :class="difficulty.color"
        >
          {{ difficulty.label }}
        </span>
      </div>
    </div>
    
    <!-- Content -->
    <div class="p-5">
      <!-- Vendor (if available) -->
      <div v-if="tour.vendor_name" class="text-xs text-gray-500 mb-2">
        Por {{ tour.vendor_name }}
      </div>
      
      <!-- Title -->
      <h3 class="font-bold text-gray-900 text-lg mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
        {{ tour.title }}
      </h3>
      
      <!-- Location -->
      <div class="flex items-center gap-1 text-sm text-gray-600 mb-3">
        <MapPin class="w-4 h-4 text-primary-500 flex-shrink-0" />
        <span class="truncate">{{ tour.location }}, {{ tour.region }}</span>
      </div>
      
      <!-- Meta Info -->
      <div class="flex items-center gap-4 text-sm text-gray-600 mb-4">
        <div class="flex items-center gap-1">
          <Clock class="w-4 h-4 text-gray-400" />
          <span>{{ formatDuration(tour.duration) }}</span>
        </div>
        <div class="flex items-center gap-1">
          <Users class="w-4 h-4 text-gray-400" />
          <span>Max {{ tour.max_group_size || 10 }}</span>
        </div>
      </div>
      
      <!-- Rating -->
      <div class="flex items-center gap-2 mb-4">
        <div class="flex items-center gap-1">
          <Star class="w-4 h-4 text-yellow-400 fill-yellow-400" />
          <span class="font-semibold text-gray-900">{{ (tour.rating ?? 0).toFixed(1) }}</span>
        </div>
        <span class="text-sm text-gray-500">({{ tour.review_count }} reseñas)</span>
      </div>
      
      <!-- Included Items (if any) -->
      <div v-if="tour.included && tour.included.length > 0" class="flex flex-wrap gap-2 mb-4">
        <span
          v-for="item in tour.included.slice(0, 3)"
          :key="item"
          class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
        >
          ✓ {{ item }}
        </span>
        <span v-if="tour.included.length > 3" class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
          +{{ tour.included.length - 3 }}
        </span>
      </div>
      
      <!-- Price & CTA -->
      <div class="flex items-end justify-between pt-4 border-t border-gray-100">
        <div>
          <div v-if="tour.original_price" class="text-sm text-gray-400 line-through">
            ${{ tour.original_price }}
          </div>
          <div class="flex items-baseline gap-1">
            <span class="text-2xl font-bold text-gray-900">${{ tour.price }}</span>
            <span class="text-sm text-gray-500">/persona</span>
          </div>
        </div>
        
        <div class="flex gap-2">
          <button
            @click="emit('view', tour.id)"
            class="px-4 py-2 text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors"
          >
            Ver detalles
          </button>
          <button
            @click="emit('book', tour.id)"
            class="px-4 py-2 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-1"
          >
            Reservar
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
