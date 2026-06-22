<script setup lang="ts">
/**
 * SearchFilters - Panel de filtros avanzados para búsqueda de tours
 * Incluye: categorías, dificultad, precio, duración, rating, región
 */
import { ref, computed } from 'vue'
import {
  SlidersHorizontal,
  X,
  ChevronDown,
  Star,
  MapPin,
  Clock,
  DollarSign,
  Mountain,
  Tag,
  Check
} from 'lucide-vue-next'
import type { SearchFilters as FiltersType } from '~/composables/useSearch'

const props = defineProps<{
  filters: FiltersType
  filterOptions: ReturnType<typeof useSearch>['filterOptions']['value']
  activeFiltersCount: number
  hasActiveFilters: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:filters': [filters: Partial<FiltersType>]
  'clear': []
  'clearFilter': [key: keyof FiltersType]
}>()

// Mobile drawer state
const isMobileOpen = ref(false)
const expandedSections = ref<Record<string, boolean>>({
  category: true,
  price: true,
  duration: false,
  difficulty: false,
  rating: false,
  region: false
})

const toggleSection = (section: string) => {
  expandedSections.value[section] = !expandedSections.value[section]
}

const updateFilter = (key: keyof FiltersType, value: any) => {
  emit('update:filters', { [key]: value })
}

const clearAll = () => {
  emit('clear')
  isMobileOpen.value = false
}

const clearSingle = (key: keyof FiltersType) => {
  emit('clearFilter', key)
}

const formatPrice = (value: number) => {
  return `$${value}`
}

const isCategoryActive = (value: string) => props.filters.category === value
const isDifficultyActive = (value: string) => props.filters.difficulty === value
const isRatingActive = (value: number) => props.filters.rating === value
const isRegionActive = (value: string) => props.filters.destination === value

const isPriceRangeActive = (min: number, max: number | null) => {
  return props.filters.minPrice === min && props.filters.maxPrice === max
}

const isDurationActive = (min: number, max: number) => {
  return props.filters.minDuration === min && props.filters.maxDuration === max
}

const filterLabelMap = computed(() => {
  const map: Record<string, string> = {}
  for (const cat of props.filterOptions.categories) {
    map[cat.value] = cat.label
  }
  for (const diff of props.filterOptions.difficulties) {
    map[diff.value] = diff.label
  }
  for (const region of props.filterOptions.regions) {
    map[region.value] = region.label
  }
  return map
})
</script>

<template>
  <div>
    <!-- Mobile Filter Button -->
    <button
      @click="isMobileOpen = true"
      class="lg:hidden fixed bottom-6 right-6 z-40 w-14 h-14 bg-primary-600 text-white rounded-full shadow-floating flex items-center justify-center gap-2 hover:bg-primary-700 transition-colors"
    >
      <SlidersHorizontal class="w-6 h-6" />
      <span
        v-if="activeFiltersCount > 0"
        class="absolute -top-1 -right-1 w-6 h-6 bg-accent-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
      >
        {{ activeFiltersCount }}
      </span>
    </button>

    <!-- Desktop Sidebar -->
    <aside class="hidden lg:block w-72 flex-shrink-0">
      <div class="sticky top-24 space-y-4">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-lg text-gray-900 flex items-center gap-2">
            <SlidersHorizontal class="w-5 h-5" />
            Filtros
          </h3>
          <button
            v-if="hasActiveFilters"
            @click="clearAll"
            class="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Limpiar
          </button>
        </div>

        <!-- Active Filters Tags -->
        <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mb-4">
          <template v-for="(value, key) in filters" :key="key">
            <span
              v-if="value && !['query', 'travelers', 'date', 'sortBy'].includes(key)"
              class="inline-flex items-center gap-1 px-3 py-1 bg-primary-50 text-primary-700 text-sm rounded-full"
            >
              {{ filterLabelMap[value as string] || value }}
              <button @click="clearSingle(key as keyof FiltersType)" class="hover:text-primary-900">
                <X class="w-3 h-3" />
              </button>
            </span>
          </template>
        </div>

        <!-- Category Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <button
            @click="toggleSection('category')"
            class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 flex items-center gap-2">
              <Tag class="w-4 h-4 text-primary-600" />
              Categoría
            </span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedSections.category }"
            />
          </button>
          <div v-show="expandedSections.category" class="px-4 pb-4">
            <div class="space-y-2">
              <button
                v-for="cat in filterOptions.categories"
                :key="cat.value"
                @click="updateFilter('category', isCategoryActive(cat.value) ? undefined : cat.value)"
                class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left"
                :class="isCategoryActive(cat.value) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
              >
                <span class="text-xl">{{ cat.icon }}</span>
                <span class="font-medium">{{ cat.label }}</span>
                <Check v-if="isCategoryActive(cat.value)" class="w-4 h-4 ml-auto text-primary-600" />
              </button>
            </div>
          </div>
        </div>

        <!-- Price Range Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <button
            @click="toggleSection('price')"
            class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 flex items-center gap-2">
              <DollarSign class="w-4 h-4 text-primary-600" />
              Precio
            </span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedSections.price }"
            />
          </button>
          <div v-show="expandedSections.price" class="px-4 pb-4">
            <div class="space-y-2">
              <button
                v-for="range in filterOptions.priceRanges"
                :key="range.label"
                @click="updateFilter('minPrice', isPriceRangeActive(range.min, range.max) ? undefined : range.min); updateFilter('maxPrice', isPriceRangeActive(range.min, range.max) ? undefined : range.max)"
                class="w-full px-3 py-2 rounded-lg transition-colors text-left font-medium"
                :class="isPriceRangeActive(range.min, range.max) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
              >
                {{ range.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- Duration Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <button
            @click="toggleSection('duration')"
            class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 flex items-center gap-2">
              <Clock class="w-4 h-4 text-primary-600" />
              Duración
            </span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedSections.duration }"
            />
          </button>
          <div v-show="expandedSections.duration" class="px-4 pb-4">
            <div class="space-y-2">
              <button
                v-for="dur in filterOptions.durations"
                :key="dur.label"
                @click="updateFilter('minDuration', isDurationActive(dur.min, dur.max) ? undefined : dur.min); updateFilter('maxDuration', isDurationActive(dur.min, dur.max) ? undefined : dur.max)"
                class="w-full px-3 py-2 rounded-lg transition-colors text-left font-medium"
                :class="isDurationActive(dur.min, dur.max) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
              >
                {{ dur.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- Difficulty Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <button
            @click="toggleSection('difficulty')"
            class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 flex items-center gap-2">
              <Mountain class="w-4 h-4 text-primary-600" />
              Dificultad
            </span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedSections.difficulty }"
            />
          </button>
          <div v-show="expandedSections.difficulty" class="px-4 pb-4">
            <div class="space-y-2">
              <button
                v-for="diff in filterOptions.difficulties"
                :key="diff.value"
                @click="updateFilter('difficulty', isDifficultyActive(diff.value) ? undefined : diff.value)"
                class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left"
                :class="isDifficultyActive(diff.value) ? 'bg-primary-50' : 'hover:bg-gray-50'"
              >
                <span
                  class="px-2 py-1 rounded text-xs font-semibold"
                  :class="diff.color"
                >
                  {{ diff.label }}
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Rating Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <button
            @click="toggleSection('rating')"
            class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 flex items-center gap-2">
              <Star class="w-4 h-4 text-primary-600" />
              Calificación
            </span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedSections.rating }"
            />
          </button>
          <div v-show="expandedSections.rating" class="px-4 pb-4">
            <div class="space-y-2">
              <button
                v-for="stars in [4, 3]"
                :key="stars"
                @click="updateFilter('rating', isRatingActive(stars) ? undefined : stars)"
                class="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors"
                :class="isRatingActive(stars) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
              >
                <div class="flex items-center gap-0.5">
                  <Star
                    v-for="n in 5"
                    :key="n"
                    class="w-4 h-4"
                    :class="n <= stars ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'"
                  />
                </div>
                <span class="font-medium">{{ stars }}+ estrellas</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Region Filter -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <button
            @click="toggleSection('region')"
            class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span class="font-semibold text-gray-900 flex items-center gap-2">
              <MapPin class="w-4 h-4 text-primary-600" />
              Región
            </span>
            <ChevronDown
              class="w-5 h-5 text-gray-400 transition-transform"
              :class="{ 'rotate-180': expandedSections.region }"
            />
          </button>
          <div v-show="expandedSections.region" class="px-4 pb-4">
            <div class="space-y-2">
              <button
                v-for="region in filterOptions.regions"
                :key="region.value"
                @click="updateFilter('destination', isRegionActive(region.value) ? undefined : region.value)"
                class="w-full px-3 py-2 rounded-lg transition-colors text-left font-medium"
                :class="isRegionActive(region.value) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
              >
                {{ region.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Mobile Drawer -->
    <Transition name="drawer">
      <div
        v-if="isMobileOpen"
        class="lg:hidden fixed inset-0 z-50 flex"
      >
        <div class="absolute inset-0 bg-black/50" @click="isMobileOpen = false" />
        <div class="relative w-80 max-w-[90vw] bg-white h-full overflow-y-auto shadow-xl">
          <div class="sticky top-0 bg-white border-b border-gray-200 z-10 px-4 py-3 flex items-center justify-between">
            <h3 class="font-bold text-lg text-gray-900 flex items-center gap-2">
              <SlidersHorizontal class="w-5 h-5" />
              Filtros
            </h3>
            <div class="flex items-center gap-2">
              <button
                v-if="hasActiveFilters"
                @click="clearAll"
                class="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Limpiar
              </button>
              <button @click="isMobileOpen = false" class="p-1 hover:bg-gray-100 rounded-lg">
                <X class="w-5 h-5 text-gray-500" />
              </button>
            </div>
          </div>
          <div class="p-4 space-y-4">
            <!-- Active Filters Tags -->
            <div v-if="hasActiveFilters" class="flex flex-wrap gap-2">
              <template v-for="(value, key) in filters" :key="key">
                <span
                  v-if="value && !['query', 'travelers', 'date', 'sortBy'].includes(key)"
                  class="inline-flex items-center gap-1 px-3 py-1 bg-primary-50 text-primary-700 text-sm rounded-full"
                >
                  {{ filterLabelMap[value as string] || value }}
                  <button @click="clearSingle(key as keyof FiltersType); isMobileOpen = false" class="hover:text-primary-900">
                    <X class="w-3 h-3" />
                  </button>
                </span>
              </template>
            </div>

            <!-- Category Filter -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <button
                @click="toggleSection('category')"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <span class="font-semibold text-gray-900 flex items-center gap-2">
                  <Tag class="w-4 h-4 text-primary-600" />
                  Categoría
                </span>
                <ChevronDown
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedSections.category }"
                />
              </button>
              <div v-show="expandedSections.category" class="px-4 pb-4">
                <div class="space-y-2">
                  <button
                    v-for="cat in filterOptions.categories"
                    :key="cat.value"
                    @click="updateFilter('category', isCategoryActive(cat.value) ? undefined : cat.value)"
                    class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left"
                    :class="isCategoryActive(cat.value) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
                  >
                    <span class="text-xl">{{ cat.icon }}</span>
                    <span class="font-medium">{{ cat.label }}</span>
                    <Check v-if="isCategoryActive(cat.value)" class="w-4 h-4 ml-auto text-primary-600" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Price Range Filter -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <button
                @click="toggleSection('price')"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <span class="font-semibold text-gray-900 flex items-center gap-2">
                  <DollarSign class="w-4 h-4 text-primary-600" />
                  Precio
                </span>
                <ChevronDown
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedSections.price }"
                />
              </button>
              <div v-show="expandedSections.price" class="px-4 pb-4">
                <div class="space-y-2">
                  <button
                    v-for="range in filterOptions.priceRanges"
                    :key="range.label"
                    @click="updateFilter('minPrice', isPriceRangeActive(range.min, range.max) ? undefined : range.min); updateFilter('maxPrice', isPriceRangeActive(range.min, range.max) ? undefined : range.max)"
                    class="w-full px-3 py-2 rounded-lg transition-colors text-left font-medium"
                    :class="isPriceRangeActive(range.min, range.max) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
                  >
                    {{ range.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Duration Filter -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <button
                @click="toggleSection('duration')"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <span class="font-semibold text-gray-900 flex items-center gap-2">
                  <Clock class="w-4 h-4 text-primary-600" />
                  Duración
                </span>
                <ChevronDown
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedSections.duration }"
                />
              </button>
              <div v-show="expandedSections.duration" class="px-4 pb-4">
                <div class="space-y-2">
                  <button
                    v-for="dur in filterOptions.durations"
                    :key="dur.label"
                    @click="updateFilter('minDuration', isDurationActive(dur.min, dur.max) ? undefined : dur.min); updateFilter('maxDuration', isDurationActive(dur.min, dur.max) ? undefined : dur.max)"
                    class="w-full px-3 py-2 rounded-lg transition-colors text-left font-medium"
                    :class="isDurationActive(dur.min, dur.max) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
                  >
                    {{ dur.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Difficulty Filter -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <button
                @click="toggleSection('difficulty')"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <span class="font-semibold text-gray-900 flex items-center gap-2">
                  <Mountain class="w-4 h-4 text-primary-600" />
                  Dificultad
                </span>
                <ChevronDown
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedSections.difficulty }"
                />
              </button>
              <div v-show="expandedSections.difficulty" class="px-4 pb-4">
                <div class="space-y-2">
                  <button
                    v-for="diff in filterOptions.difficulties"
                    :key="diff.value"
                    @click="updateFilter('difficulty', isDifficultyActive(diff.value) ? undefined : diff.value)"
                    class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left"
                    :class="isDifficultyActive(diff.value) ? 'bg-primary-50' : 'hover:bg-gray-50'"
                  >
                    <span class="px-2 py-1 rounded text-xs font-semibold" :class="diff.color">
                      {{ diff.label }}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Rating Filter -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <button
                @click="toggleSection('rating')"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <span class="font-semibold text-gray-900 flex items-center gap-2">
                  <Star class="w-4 h-4 text-primary-600" />
                  Calificación
                </span>
                <ChevronDown
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedSections.rating }"
                />
              </button>
              <div v-show="expandedSections.rating" class="px-4 pb-4">
                <div class="space-y-2">
                  <button
                    v-for="stars in [4, 3]"
                    :key="stars"
                    @click="updateFilter('rating', isRatingActive(stars) ? undefined : stars)"
                    class="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors"
                    :class="isRatingActive(stars) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
                  >
                    <div class="flex items-center gap-0.5">
                      <Star v-for="n in 5" :key="n" class="w-4 h-4" :class="n <= stars ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'" />
                    </div>
                    <span class="font-medium">{{ stars }}+ estrellas</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Region Filter -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <button
                @click="toggleSection('region')"
                class="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
              >
                <span class="font-semibold text-gray-900 flex items-center gap-2">
                  <MapPin class="w-4 h-4 text-primary-600" />
                  Región
                </span>
                <ChevronDown
                  class="w-5 h-5 text-gray-400 transition-transform"
                  :class="{ 'rotate-180': expandedSections.region }"
                />
              </button>
              <div v-show="expandedSections.region" class="px-4 pb-4">
                <div class="space-y-2">
                  <button
                    v-for="region in filterOptions.regions"
                    :key="region.value"
                    @click="updateFilter('destination', isRegionActive(region.value) ? undefined : region.value)"
                    class="w-full px-3 py-2 rounded-lg transition-colors text-left font-medium"
                    :class="isRegionActive(region.value) ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-50 text-gray-700'"
                  >
                    {{ region.label }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Apply Button -->
            <button
              @click="isMobileOpen = false"
              class="w-full py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors"
            >
              Ver resultados
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.drawer-enter-active {
  transition: opacity 0.3s ease;
}
.drawer-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-active > div:last-child {
  animation: slide-in 0.3s ease;
}
.drawer-leave-active > div:last-child {
  animation: slide-out 0.2s ease;
}
@keyframes slide-in {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
@keyframes slide-out {
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
}
</style>
