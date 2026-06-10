<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  MapPin, 
  Calendar, 
  Users, 
  Search, 
  Map, 
  ArrowRight, 
  Check 
} from 'lucide-vue-next'
import { DESTINATIONS } from '~/config/constants'

const { t } = useI18n()

const isVideoLoaded = ref(false)
const showSearch = ref(false)
const isSearching = ref(false)
const searchForm = ref({
  destination: '',
  dates: '',
  travelers: '2'
})

// Destination suggestions using centralized constants with i18n
const destinations = [
  { name: 'Guanacaste', region: t('hero.destinations.guanacaste.region'), icon: '🏖️', slug: 'guanacaste' },
  { name: 'La Fortuna / Arenal', region: t('hero.destinations.lafortuna.region'), icon: '🌋', slug: 'la-fortuna' },
  { name: 'Monteverde', region: t('hero.destinations.monteverde.region'), icon: '🌲', slug: 'monteverde' },
  { name: 'Manuel Antonio', region: t('hero.destinations.manuelantonio.region'), icon: '🐒', slug: 'manuel-antonio' },
  { name: 'Puerto Viejo', region: t('hero.destinations.puertoviejo.region'), icon: '🏄', slug: 'caribe' },
  { name: 'San José', region: t('hero.destinations.sanjose.region'), icon: '🏛️', slug: 'valle-central' }
].filter(d => DESTINATIONS.list.some(cd => cd.slug === d.slug))

// Traveler options from i18n
const travelerOptions = [
  { value: '1', label: t('search.travelers.1') },
  { value: '2', label: t('search.travelers.2') },
  { value: '3', label: t('search.travelers.3') },
  { value: '4', label: t('search.travelers.4') },
  { value: '5+', label: t('search.travelers.5plus') }
]

// Live activity state - SSR-safe with client-only random updates
const MOCK_ACTIVITY_BASE = 120
const liveActivity = ref({
  usersOnline: MOCK_ACTIVITY_BASE, // Valor fijo para SSR
  recentBooking: { user: t('hero.live.mockUser'), destination: t('hero.live.mockDestination'), time: '2 min' }
})

let liveInterval: ReturnType<typeof setInterval>

onMounted(() => {
  setTimeout(() => showSearch.value = true, 300)
  
  // Actualizar con valor aleatorio solo en cliente (evita hydration mismatch)
  liveActivity.value.usersOnline = MOCK_ACTIVITY_BASE + Math.floor(Math.random() * 30)
  
  liveInterval = setInterval(() => {
    liveActivity.value.usersOnline = MOCK_ACTIVITY_BASE + Math.floor(Math.random() * 30)
  }, 10000)
})

onUnmounted(() => {
  if (liveInterval) clearInterval(liveInterval)
})

const handleSearch = async () => {
  if (!searchForm.value.destination) {
    return
  }
  
  isSearching.value = true
  
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const query = new URLSearchParams({
    destination: searchForm.value.destination,
    dates: searchForm.value.dates,
    travelers: searchForm.value.travelers
  }).toString()
  
  window.location.href = `/tours?${query}`
}
</script>

<template>
  <section class="relative min-h-screen flex items-center overflow-hidden">
    <!-- Video Background with Fallback -->
    <div class="absolute inset-0 z-0">
      <video
        autoplay
        muted
        loop
        playsinline
        poster="https://images.unsplash.com/photo-1518638150340-f706e86654de?w=1920&q=80"
        class="w-full h-full object-cover transition-opacity duration-1000"
        :class="{ 'opacity-100': isVideoLoaded, 'opacity-0': !isVideoLoaded }"
        @loadeddata="isVideoLoaded = true"
      >
        <source src="https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-beach-with-waves-1089-large.mp4" type="video/mp4">
      </video>
      <NuxtImg 
        v-show="!isVideoLoaded"
        src="https://images.unsplash.com/photo-1518638150340-f706e86654de?w=1920&q=80"
        class="absolute inset-0 w-full h-full object-cover"
        :alt="t('hero.video.fallbackAlt')"
        width="1920"
        height="1080"
        format="webp"
      ></NuxtImg>
      <div class="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/40"></div>
      <div class="absolute bottom-0 inset-x-0 h-24 bg-gradient-to-t from-black/30 to-transparent"></div>
    </div>

    <!-- Content -->
    <div class="relative z-10 container mx-auto px-4 pt-20 pb-32">
      <div class="max-w-5xl mx-auto text-center">
        
        <!-- Live Activity Badge -->
        <Transition
          enter="transition-all duration-700 ease-out"
          enter-from="opacity-0 -translate-y-4"
          enter-to="opacity-100 translate-y-0"
        >
          <div 
            v-show="showSearch"
            class="inline-flex items-center gap-3 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full text-white text-sm mb-6 border border-white/20"
          >
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 bg-accent-400 rounded-full animate-pulse"></span>
              <span class="font-medium text-accent-300">{{ liveActivity.usersOnline }}</span>
              <span class="text-white/80">{{ t('hero.live.usersOnline') }}</span>
            </div>
            <span class="text-white/40">|</span>
            <div class="flex items-center gap-1.5 text-xs text-white/70">
              <span class="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
              <span>{{ t('hero.live.recentBooking', { user: liveActivity.recentBooking.user, destination: liveActivity.recentBooking.destination }) }}</span>
            </div>
          </div>
        </Transition>

        <!-- Main Headline -->
        <Transition
          enter="transition-all duration-700 delay-100 ease-out"
          enter-from="opacity-0 translate-y-8 scale-95"
          enter-to="opacity-100 translate-y-0 scale-100"
        >
          <h1 
            v-show="showSearch"
            class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-[1.1] tracking-tight"
          >
            <span class="block">{{ t('hero.headline.line1') }}</span>
            <span class="gradient-text bg-gradient-to-r from-primary-300 via-accent-300 to-secondary-300 bg-clip-text text-transparent">
              {{ t('hero.headline.line2') }}
            </span>
          </h1>
        </Transition>

        <!-- Subtitle -->
        <Transition
          enter="transition-all duration-700 delay-200 ease-out"
          enter-from="opacity-0 translate-y-6"
          enter-to="opacity-100 translate-y-0"
        >
          <p 
            v-show="showSearch"
            class="text-xl md:text-2xl text-white/90 mb-10 max-w-2xl mx-auto leading-relaxed font-light"
          >
            {{ t('hero.subtitle.main') }}
            <span class="text-primary-300 font-medium">{{ t('hero.subtitle.highlight') }}</span>
          </p>
        </Transition>

        <!-- Search Bar -->
        <Transition
          enter="transition-all duration-700 delay-300 ease-out"
          enter-from="opacity-0 translate-y-8 scale-95"
          enter-to="opacity-100 translate-y-0 scale-100"
        >
          <div 
            v-show="showSearch"
            class="bg-white/95 backdrop-blur-xl rounded-2xl shadow-floating p-2 md:p-4 mb-8 max-w-4xl mx-auto"
          >
            <div class="grid md:grid-cols-4 gap-2 md:gap-3">
              <!-- Destination -->
              <div class="relative group">
                <label class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider pl-1">
                  {{ t('hero.search.destination.label') }}
                </label>
                <div class="relative">
                  <select 
                    v-model="searchForm.destination"
                    class="w-full px-4 py-3.5 bg-gray-50 border-2 border-transparent hover:border-primary-200 focus:border-primary-500 focus:bg-white rounded-xl transition-all duration-200 appearance-none cursor-pointer text-gray-800 font-medium"
                  >
                    <option value="">{{ t('hero.search.destination.placeholder') }}</option>
                    <option v-for="dest in destinations" :key="dest.name" :value="dest.name">
                      {{ dest.icon }} {{ dest.name }}
                    </option>
                  </select>
                  <MapPin class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none group-focus-within:text-primary-500 transition-colors" />
                </div>
              </div>

              <!-- Dates -->
              <div class="relative group">
                <label class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider pl-1">
                  {{ t('hero.search.dates.label') }}
                </label>
                <div class="relative">
                  <input 
                    v-model="searchForm.dates"
                    type="text"
                    :placeholder="t('hero.search.dates.placeholder')"
                    class="w-full px-4 py-3.5 bg-gray-50 border-2 border-transparent hover:border-primary-200 focus:border-primary-500 focus:bg-white rounded-xl transition-all duration-200 text-gray-800 font-medium"
                    @focus="$event.target.type='date'"
                    @blur="$event.target.type='text'"
                  />
                  <Calendar class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none group-focus-within:text-primary-500 transition-colors" />
                </div>
              </div>

              <!-- Travelers -->
              <div class="relative group">
                <label class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wider pl-1">
                  {{ t('hero.search.travelers.label') }}
                </label>
                <div class="relative">
                  <select 
                    v-model="searchForm.travelers"
                    class="w-full px-4 py-3.5 bg-gray-50 border-2 border-transparent hover:border-primary-200 focus:border-primary-500 focus:bg-white rounded-xl transition-all duration-200 appearance-none cursor-pointer text-gray-800 font-medium"
                  >
                    <option v-for="opt in travelerOptions" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                  <Users class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none group-focus-within:text-primary-500 transition-colors" />
                </div>
              </div>

              <!-- Search Button -->
              <div class="flex items-end">
                <button 
                  @click="handleSearch"
                  :disabled="isSearching"
                  class="w-full px-6 py-3.5 bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white font-bold rounded-xl transition-all duration-300 shadow-elevated hover:shadow-floating active:scale-[0.98] flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed group"
                  :aria-label="t('hero.search.button')"
                >
                  <Search class="w-5 h-5 group-hover:scale-110 transition-transform" />
                  <span v-if="!isSearching">{{ t('hero.search.button') }}</span>
                  <span v-else class="flex items-center gap-2">
                    <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ t('hero.search.searching') }}
                  </span>
                </button>
              </div>
            </div>
            
            <!-- Quick Links -->
            <div class="flex flex-wrap items-center justify-center gap-2 mt-3 pt-3 border-t border-gray-100">
              <span class="text-xs text-gray-500">{{ t('hero.search.popular') }}</span>
              <NuxtLink 
                v-for="dest in destinations.slice(0, 3)" 
                :key="dest.name"
                :to="`/destinos/${dest.slug}`"
                class="text-xs px-3 py-1 bg-gray-100 hover:bg-primary-100 text-gray-600 hover:text-primary-700 rounded-full transition-colors"
              >
                {{ dest.name }}
              </NuxtLink>
            </div>
          </div>
        </Transition>

        <!-- CTA Buttons -->
        <Transition
          enter="transition-all duration-700 delay-400 ease-out"
          enter-from="opacity-0 translate-y-6"
          enter-to="opacity-100 translate-y-0"
        >
          <div 
            v-show="showSearch"
            class="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <NuxtLink 
              to="/planificador" 
              class="group btn btn-lg bg-white/95 text-gray-900 hover:bg-white rounded-full shadow-elevated hover:shadow-floating transition-all duration-300"
            >
              <Map class="w-5 h-5 text-primary-600 group-hover:scale-110 transition-transform" />
              <span>{{ t('hero.cta.planner') }}</span>
              <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </NuxtLink>
            
            <NuxtLink 
              to="/destinos" 
              class="group btn btn-lg bg-white/10 backdrop-blur-sm border-2 border-white text-white hover:bg-white/20 hover:border-white/40 rounded-full transition-all duration-300"
            >
              <span>{{ t('hero.cta.explore') }}</span>
              <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </NuxtLink>
          </div>
        </Transition>

        <!-- Trust Indicators -->
        <Transition
          enter="transition-all duration-700 delay-500 ease-out"
          enter-from="opacity-0 translate-y-4"
          enter-to="opacity-100 translate-y-0"
        >
          <div 
            v-show="showSearch"
            class="mt-10 flex flex-wrap items-center justify-center gap-6 md:gap-8 text-white/80 text-sm"
          >
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center">
                <Check class="w-4 h-4 text-accent-300" />
              </div>
              <span class="text-white/90">{{ t('hero.trust.cancelation') }}</span>
            </div>
            
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-secondary-500/20 rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-secondary-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <span class="text-white/90">{{ t('hero.trust.bestPrice') }}</span>
            </div>
            
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-primary-500/20 rounded-full flex items-center justify-center">
                <Users class="w-4 h-4 text-primary-300" />
              </div>
              <span class="text-white/90">{{ t('hero.trust.travelers') }}</span>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Scroll Indicator -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 animate-bounce-slow">
      <div 
        class="w-12 h-12 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full flex items-center justify-center cursor-pointer hover:bg-white/20 transition-colors"
        role="button"
        tabindex="0"
        :aria-label="t('hero.scrollIndicator.label')"
      >
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
        </svg>
      </div>
    </div>
  </section>
</template>
