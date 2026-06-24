<template>
  <div class="relative">
    <div
      class="fixed top-0 left-0 right-0 h-[3px] z-[100] bg-gradient-to-r from-primary-500 via-accent-400 to-secondary-500 transition-all duration-150 origin-left"
      :style="{ transform: `scaleX(${scrollProgress / 100})` }"
    />

    <HeroSectionV2 />

    <TrustLogos />

    <StatsSectionV2 />

    <section class="relative py-28 overflow-hidden bg-white dark:bg-gray-950">
      <div class="absolute inset-0 bg-gradient-to-b from-primary-50/30 via-transparent to-transparent dark:from-primary-950/10" />
      <div class="absolute top-20 right-10 w-72 h-72 bg-primary-200/20 dark:bg-primary-800/10 rounded-full blur-3xl" />
      <div class="absolute bottom-20 left-10 w-96 h-96 bg-emerald-200/20 dark:bg-emerald-800/10 rounded-full blur-3xl" />

      <div class="container mx-auto px-4 relative z-10">
        <div class="text-center mb-16">
          <span class="inline-flex items-center gap-2 px-5 py-2 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-semibold rounded-full text-sm">
            <MapPin class="w-4 h-4" />
            Explora Costa Rica
          </span>
          <h2 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mt-6 mb-4">
            Destinos que<span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-emerald-500 dark:from-primary-400 dark:to-emerald-400"> enamoran</span>
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            De costa a costa, descubre paisajes que quitan el aliento
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-6 lg:gap-8">
          <NuxtLink
            v-for="(dest, i) in activeDestinations"
            :key="dest.id"
            :to="`/destinos/${dest.slug}`"
            class="group relative h-96 rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-700 cursor-pointer"
            :style="{ transitionDelay: `${i * 80}ms` }"
          >
            <NuxtImg
              :src="dest.image"
              :alt="dest.name"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
              width="800"
              height="700"
              format="webp"
              loading="lazy"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
            <div class="absolute inset-0 bg-primary-600/0 group-hover:bg-primary-600/20 transition-colors duration-500" />

            <div class="absolute top-5 left-5">
              <span class="px-4 py-2 bg-white/10 backdrop-blur-md text-white text-xs font-semibold rounded-full border border-white/20 flex items-center gap-2">
                <MapPin class="w-3.5 h-3.5" />
                {{ dest.region }}
              </span>
            </div>

            <div class="absolute bottom-0 left-0 right-0 p-8">
              <h3 class="text-white text-2xl font-bold mb-2">{{ dest.name }}</h3>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="flex">
                    <Star v-for="s in 5" :key="s" class="w-4 h-4" :class="s <= Math.floor(Number(dest.rating)) ? 'text-amber-400 fill-amber-400' : 'text-white/20'" />
                  </div>
                  <span class="text-white/80 text-sm font-medium">{{ dest.rating }}</span>
                </div>
                <span class="text-white/70 text-sm font-medium flex items-center gap-2 group-hover:gap-3 transition-all">
                  Explorar
                  <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
              </div>
            </div>
          </NuxtLink>
        </div>

        <div class="text-center mt-12">
          <NuxtLink to="/destinos" class="group inline-flex items-center gap-3 px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-2xl transition-all shadow-lg hover:shadow-xl active:scale-[0.98]">
            <span>Descubrir todos los destinos</span>
            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="relative py-28 overflow-hidden bg-gray-50 dark:bg-gray-900">
      <div class="absolute inset-0 bg-gradient-to-b from-amber-50/30 via-transparent to-transparent dark:from-amber-950/10" />
      <div class="absolute top-40 -left-20 w-80 h-80 bg-amber-200/20 dark:bg-amber-800/10 rounded-full blur-3xl" />

      <div class="container mx-auto px-4 relative z-10">
        <div class="flex flex-col lg:flex-row lg:items-end justify-between mb-16 gap-6">
          <div>
            <span class="inline-flex items-center gap-2 px-5 py-2 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 font-semibold rounded-full text-sm">
              <Building2 class="w-4 h-4" />
              Alojamientos
            </span>
            <h2 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mt-6">
              Donde<span class="text-amber-600 dark:text-amber-400"> descansar</span>
            </h2>
          </div>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-md">
            Hoteles boutique, eco-lodges y resorts frente al mar para cada estilo de viajero
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          <NuxtLink
            v-for="(prop, i) in activeProperties"
            :key="prop.id"
            :to="`/hoteles/${prop.slug}`"
            class="group bg-white dark:bg-gray-800 rounded-3xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-500"
            :class="i === 0 ? 'lg:col-span-2' : ''"
            :style="{ transitionDelay: `${i * 80}ms` }"
          >
            <div :class="['relative overflow-hidden', i === 0 ? 'h-72 lg:h-80' : 'h-56']">
              <NuxtImg
                :src="prop.cover_image || prop.image"
                :alt="prop.name"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                width="800"
                height="500"
                format="webp"
                loading="lazy"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div class="absolute top-4 right-4">
                <span class="px-4 py-2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm text-gray-800 dark:text-white text-xs font-bold rounded-full shadow-lg">
                  {{ prop.property_type || 'Hotel' }}
                </span>
              </div>
              <div v-if="i === 0" class="absolute top-4 left-4">
                <span class="px-4 py-2 bg-amber-500 text-white text-xs font-bold rounded-full shadow-lg animate-pulse">
                  ★ Recomendado
                </span>
              </div>
            </div>
            <div class="p-6 lg:p-8">
              <h3 class="font-bold text-gray-900 dark:text-white text-xl mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {{ prop.name }}
              </h3>
              <p class="text-gray-600 dark:text-gray-400 text-sm flex items-center gap-1.5 mb-4">
                <MapPin class="w-4 h-4 text-gray-400" />
                {{ prop.region }}
              </p>
              <div class="flex items-center justify-between pt-5 border-t border-gray-100 dark:border-gray-700">
                <div>
                  <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">${{ prop.base_price || prop.price || 89 }}</span>
                  <span class="text-gray-500 dark:text-gray-500 text-sm">/noche</span>
                </div>
                <div class="flex items-center gap-2">
                  <div class="flex">
                    <Star v-for="s in 5" :key="s" class="w-4 h-4" :class="s <= Math.floor(Number(prop.rating || 4.5)) ? 'text-amber-400 fill-amber-400' : 'text-gray-200 dark:text-gray-600'" />
                  </div>
                  <span class="font-semibold text-gray-700 dark:text-gray-300">{{ prop.rating || '4.5' }}</span>
                </div>
              </div>
            </div>
          </NuxtLink>
        </div>

        <div class="text-center mt-12">
          <NuxtLink to="/hoteles" class="group inline-flex items-center gap-3 px-8 py-4 bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 font-bold rounded-2xl border-2 border-primary-600 dark:border-primary-500 hover:bg-primary-600 dark:hover:bg-primary-600 hover:text-white dark:hover:text-white transition-all shadow-lg hover:shadow-xl">
            <span>Explorar hoteles</span>
            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="relative py-28 overflow-hidden bg-white dark:bg-gray-950">
      <div class="absolute inset-0 bg-gradient-to-b from-emerald-50/30 via-transparent to-transparent dark:from-emerald-950/10" />
      <div class="absolute bottom-20 right-10 w-80 h-80 bg-emerald-200/20 dark:bg-emerald-800/10 rounded-full blur-3xl" />

      <div class="container mx-auto px-4 relative z-10">
        <div class="text-center mb-16">
          <span class="inline-flex items-center gap-2 px-5 py-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 font-semibold rounded-full text-sm">
            <Compass class="w-4 h-4" />
            Experiencias
          </span>
          <h2 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mt-6 mb-4">
            Aventuras que<span class="text-emerald-600 dark:text-emerald-400"> transforman</span>
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Desde canopy en la selva hasta avistamiento de ballenas en el Pacífico
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-6 lg:gap-8">
          <NuxtLink
            v-for="(tour, i) in activeTours"
            :key="tour.id"
            :to="`/tours/${tour.slug}`"
            class="group bg-white dark:bg-gray-800 rounded-3xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-500 border border-gray-100 dark:border-gray-700/50"
            :style="{ transitionDelay: `${i * 80}ms` }"
          >
            <div class="relative h-56 overflow-hidden">
              <NuxtImg
                :src="tour.cover_image || tour.image"
                :alt="tour.name"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                width="800"
                height="450"
                format="webp"
                loading="lazy"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div class="absolute top-4 left-4">
                <span class="px-4 py-2 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm text-gray-800 dark:text-white text-xs font-bold rounded-full shadow-lg flex items-center gap-2">
                  <Clock class="w-3.5 h-3.5" />
                  {{ tour.duration_text || (tour.duration_hours ? tour.duration_hours + 'h' : 'Full Day') }}
                </span>
              </div>
              <div class="absolute top-4 right-4">
                <span class="px-4 py-2 bg-amber-500/90 backdrop-blur-sm text-white text-xs font-bold rounded-full shadow-lg uppercase tracking-wider">
                  {{ tour.category || 'Aventura' }}
                </span>
              </div>
            </div>
            <div class="p-6">
              <h3 class="font-bold text-gray-900 dark:text-white text-xl mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {{ tour.name }}
              </h3>
              <p class="text-gray-600 dark:text-gray-400 text-sm mb-4 flex items-center gap-1.5">
                <MapPin class="w-4 h-4 text-gray-400" />
                {{ tour.location || 'Costa Rica' }}
              </p>
              <div class="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700">
                <div>
                  <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">${{ tour.price || 65 }}</span>
                  <span class="text-gray-500 dark:text-gray-500 text-sm">/persona</span>
                </div>
                <div class="flex items-center gap-3">
                  <div class="flex items-center gap-1">
                    <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                    <span class="font-semibold text-gray-700 dark:text-gray-300">{{ tour.rating || '4.7' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </NuxtLink>
        </div>

        <div class="text-center mt-12">
          <NuxtLink to="/tours" class="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-emerald-600 to-primary-600 hover:from-emerald-500 hover:to-primary-500 text-white font-bold rounded-2xl transition-all shadow-lg hover:shadow-xl active:scale-[0.98]">
            <span>Ver todos los tours</span>
            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </NuxtLink>
        </div>
      </div>
    </section>

    <WhyCostaRica />

    <ExperiencesSection />

    <GallerySection />

    <TestimonialsSection />

    <FeaturedPackages />

    <FAQSection />

    <section class="relative py-28 overflow-hidden bg-gray-900 dark:bg-gray-950">
      <div class="absolute inset-0 bg-gradient-to-br from-primary-900 via-gray-900 to-emerald-900 dark:from-primary-950 dark:via-gray-950 dark:to-emerald-950" />
      <div class="absolute inset-0 opacity-20">
        <div class="absolute top-0 right-0 w-[40rem] h-[40rem] bg-primary-500 rounded-full blur-[120px] translate-x-1/2 -translate-y-1/2" />
        <div class="absolute bottom-0 left-0 w-[40rem] h-[40rem] bg-emerald-500 rounded-full blur-[120px] -translate-x-1/2 translate-y-1/2" />
      </div>

      <div class="container mx-auto px-4 relative z-10 text-center">
        <div class="inline-flex items-center gap-2 px-5 py-2 bg-white/10 backdrop-blur-sm text-primary-300 font-semibold rounded-full text-sm border border-white/10 mb-8">
          <Sparkles class="w-4 h-4" />
          Empieza tu viaje hoy
        </div>

        <h2 class="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
          ¿Listo para tu<br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-300 via-emerald-300 to-amber-300">aventura en Costa Rica</span>?
        </h2>
        <p class="text-xl text-white/70 mb-12 max-w-lg mx-auto">
          Únete a miles de viajeros que ya descubrieron el paraíso. Tu aventura comienza aquí.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <NuxtLink to="/register" class="group inline-flex items-center gap-3 px-10 py-5 bg-white text-gray-900 font-bold rounded-2xl hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl text-lg active:scale-[0.98]">
            <UserPlus class="w-5 h-5" />
            Crear cuenta gratis
            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </NuxtLink>
          <NuxtLink to="/planificador" class="group inline-flex items-center gap-3 px-10 py-5 bg-white/10 backdrop-blur-sm border-2 border-white/30 text-white font-bold rounded-2xl hover:bg-white/20 hover:border-white/50 transition-all text-lg active:scale-[0.98]">
            <Map class="w-5 h-5" />
            Planificar mi viaje
          </NuxtLink>
        </div>

        <div class="mt-12 flex flex-wrap items-center justify-center gap-8 text-white/60 text-sm">
          <div class="flex items-center gap-2">
            <CheckCircle class="w-4 h-4 text-emerald-400" />
            Cancelación gratuita 48h
          </div>
          <div class="flex items-center gap-2">
            <CheckCircle class="w-4 h-4 text-emerald-400" />
            Mejor precio garantizado
          </div>
          <div class="flex items-center gap-2">
            <CheckCircle class="w-4 h-4 text-emerald-400" />
            +10,000 viajeros felices
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  MapPin, Building2, Compass,
  Star, ArrowRight, Clock, UserPlus, Map, CheckCircle, Sparkles
} from 'lucide-vue-next'

const config = useRuntimeConfig()

const { scrollProgress } = useScrollProgress()

const { data: landingData } = useFetch(
  () => `${config.public.apiBase}/landing/content`,
  { key: 'landing-content', default: () => null }
)

const activeDestinations = computed(() => {
  if (landingData.value?.destinations?.length) {
    return landingData.value.destinations.map((d: any) => ({
      ...d, rating: d.rating || '4.8'
    }))
  }
  return defaultDestinations
})

const activeProperties = computed(() => {
  if (landingData.value?.properties?.length) {
    return landingData.value.properties
  }
  return defaultProperties
})

const activeTours = computed(() => {
  if (landingData.value?.tours?.length) {
    return landingData.value.tours
  }
  return defaultTours
})

const defaultDestinations = [
  {
    id: 1, slug: 'la-fortuna', name: 'La Fortuna',
    image: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907',
    region: 'Alajuela', rating: '4.8'
  },
  {
    id: 2, slug: 'monteverde', name: 'Monteverde',
    image: 'https://images.unsplash.com/photo-1518638150340-f706e86654de',
    region: 'Puntarenas', rating: '4.7'
  },
  {
    id: 3, slug: 'manuel-antonio', name: 'Manuel Antonio',
    image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5',
    region: 'Puntarenas', rating: '4.9'
  }
]

const defaultProperties = [
  {
    id: 1, slug: 'nayara-resort', name: 'Nayara Resort',
    cover_image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945',
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945',
    region: 'La Fortuna', property_type: 'Resort', base_price: 249, rating: 4.9
  },
  {
    id: 2, slug: 'monteverde-lodge', name: 'Monteverde Lodge',
    cover_image: 'https://images.unsplash.com/photo-1540541338287-41795007eca6',
    image: 'https://images.unsplash.com/photo-1540541338287-41795007eca6',
    region: 'Monteverde', property_type: 'Eco-Lodge', base_price: 159, rating: 4.7
  },
  {
    id: 3, slug: 'manuel-antonio-hotel', name: 'Hotel Parador',
    cover_image: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4',
    image: 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4',
    region: 'Manuel Antonio', property_type: 'Hotel', base_price: 189, rating: 4.8
  }
]

const defaultTours = [
  {
    id: 1, slug: 'rafting-pacuare', name: 'Rafting Río Pacuare',
    cover_image: 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7',
    image: 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7',
    location: 'Turrialba', category: 'Aventura', price: 95, rating: 4.9, duration_hours: 8, duration_text: 'Full Day'
  },
  {
    id: 2, slug: 'canopy-monteverde', name: 'Canopy Monteverde',
    cover_image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5',
    image: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5',
    location: 'Monteverde', category: 'Aventura', price: 65, rating: 4.8, duration_hours: 3, duration_text: '3h'
  },
  {
    id: 3, slug: 'whale-watching', name: 'Avistamiento de Ballenas',
    cover_image: 'https://images.unsplash.com/photo-1560275619-4cc5fa59b650',
    image: 'https://images.unsplash.com/photo-1560275619-4cc5fa59b650',
    location: 'Uvita', category: 'Naturaleza', price: 75, rating: 4.7, duration_hours: 4, duration_text: '4h'
  }
]
</script>
