<template>
  <div>
    <!-- Hero Section -->
    <section class="relative min-h-[85vh] flex items-center overflow-hidden">
      <!-- Background -->
      <div class="absolute inset-0 bg-gradient-to-br from-teal-900 via-teal-800 to-emerald-900"></div>
      <div class="absolute inset-0">
        <NuxtImg 
          src="https://images.unsplash.com/photo-1518638150340-f706e86654de?w=1920&q=80" 
          alt="Costa Rica" 
          class="w-full h-full object-cover"
          width="1920"
          height="1080"
          format="webp"
        />
      </div>
      <div class="absolute inset-0 bg-gradient-to-t from-teal-950/90 via-teal-900/60 to-transparent"></div>
      
      <!-- Decorative Elements -->
      <div class="absolute top-20 left-10 w-72 h-72 bg-teal-400/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl"></div>
      
      <!-- Content -->
      <div class="relative z-10 container mx-auto px-4 py-20">
        <div class="max-w-4xl mx-auto text-center">
          <span class="inline-flex items-center gap-2 px-5 py-2 bg-white/10 backdrop-blur-sm text-white text-sm font-medium rounded-full mb-8 border border-white/20">
            <MapPin class="w-4 h-4 text-teal-300" />
            Descubre el Paraíso de Centro América
          </span>
          
          <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight tracking-tight">
            Vive la Aventura en
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-teal-300 to-emerald-300">Costa Rica</span>
          </h1>
          
          <p class="text-xl md:text-2xl text-white/90 mb-12 max-w-2xl mx-auto leading-relaxed">
            Playas pristine, volcanes activos, selvas tropicales y experiencias únicas te esperan.
          </p>

          <!-- Search Box -->
          <div class="bg-white/95 backdrop-blur-xl rounded-2xl p-3 shadow-2xl max-w-4xl mx-auto border border-white/20">
            <div class="grid md:grid-cols-5 gap-3">
              <div class="md:col-span-2 p-4">
                <label class="text-xs text-gray-700 font-semibold block mb-2 uppercase tracking-wide">Destino</label>
                <input 
                  v-model="search.destino" 
                  type="text" 
                  placeholder="¿A dónde vas?" 
                  class="w-full text-gray-800 placeholder-gray-400 outline-none font-medium bg-transparent text-base"
                />
              </div>
              <div class="p-4 border-l border-gray-100">
                <label class="text-xs text-gray-700 font-semibold block mb-2 uppercase tracking-wide">Check-in</label>
                <input 
                  v-model="search.checkin" 
                  type="date" 
                  class="w-full text-gray-800 outline-none font-medium bg-transparent text-base"
                />
              </div>
              <div class="p-4 border-l border-gray-100">
                <label class="text-xs text-gray-700 font-semibold block mb-2 uppercase tracking-wide">Check-out</label>
                <input 
                  v-model="search.checkout" 
                  type="date" 
                  class="w-full text-gray-800 outline-none font-medium bg-transparent text-base"
                />
              </div>
              <button 
                @click="buscar" 
                class="bg-teal-600 text-white font-bold py-4 px-8 rounded-xl hover:bg-teal-700 active:bg-teal-800 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                <Search class="w-5 h-5" />
                <span>Buscar</span>
              </button>
            </div>
          </div>

          <!-- Quick Links -->
          <div class="mt-10 flex flex-wrap justify-center gap-4">
            <NuxtLink to="/destinos" class="group flex items-center gap-2 px-5 py-3 bg-white/10 backdrop-blur-sm text-white rounded-full text-sm font-medium hover:bg-white/20 transition-all border border-white/10 hover:border-white/30">
              <Mountain class="w-4 h-4" />
              <span>Destinos</span>
            </NuxtLink>
            <NuxtLink to="/hoteles" class="group flex items-center gap-2 px-5 py-3 bg-white/10 backdrop-blur-sm text-white rounded-full text-sm font-medium hover:bg-white/20 transition-all border border-white/10 hover:border-white/30">
              <Building2 class="w-4 h-4" />
              <span>Hoteles</span>
            </NuxtLink>
            <NuxtLink to="/tours" class="group flex items-center gap-2 px-5 py-3 bg-white/10 backdrop-blur-sm text-white rounded-full text-sm font-medium hover:bg-white/20 transition-all border border-white/10 hover:border-white/30">
              <Compass class="w-4 h-4" />
              <span>Tours</span>
            </NuxtLink>
            <NuxtLink to="/planificador" class="group flex items-center gap-2 px-5 py-3 bg-white/10 backdrop-blur-sm text-white rounded-full text-sm font-medium hover:bg-white/20 transition-all border border-white/10 hover:border-white/30">
              <FileText class="w-4 h-4" />
              <span>Planificador</span>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div class="w-8 h-12 border-2 border-white/40 rounded-full flex justify-center pt-2">
          <div class="w-1.5 h-3 bg-white rounded-full animate-pulse"></div>
        </div>
      </div>
    </section>

    <!-- Loading / Skeleton -->
    <div v-if="pending" class="py-24 bg-gray-50">
      <div class="container mx-auto px-4">
        <div class="grid md:grid-cols-3 gap-8">
          <div v-for="i in 3" :key="i" class="bg-white rounded-2xl overflow-hidden shadow-lg">
            <div class="h-64 bg-gray-200 animate-pulse"></div>
            <div class="p-6 space-y-4">
              <div class="h-6 bg-gray-200 rounded w-3/4 animate-pulse"></div>
              <div class="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <template v-if="!pending && landingData">
      <!-- Trust Section -->
      <TrustLogos />

      <!-- Destinations Section -->
      <section class="py-24 bg-white">
        <div class="container mx-auto px-4">
          <div class="text-center mb-16">
            <span class="inline-block px-4 py-1.5 bg-teal-100 text-teal-700 text-sm font-semibold rounded-full mb-4">Explora Costa Rica</span>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Destinos Populares
            </h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Explora las regiones más impresionantes del país
            </p>
          </div>
          
          <div class="grid md:grid-cols-3 gap-8">
            <NuxtLink 
              v-for="dest in landingData?.destinations" 
              :key="dest.id" 
              :to="`/destinos/${dest.slug}`" 
              class="group relative h-80 rounded-2xl overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer"
            >
              <NuxtImg 
                :src="dest.image || 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=800&q=80'" 
                :alt="dest.name"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                width="800"
                height="600"
                format="webp"
                :placeholder="true"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"></div>
              <div class="absolute bottom-0 left-0 right-0 p-8">
                <span class="inline-flex items-center gap-1 text-white/80 text-sm font-medium mb-2">
                  <MapPin class="w-4 h-4" />
                  {{ dest.region }}
                </span>
                <h3 class="text-white text-2xl font-bold mb-3">{{ dest.name }}</h3>
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-1">
                    <Star class="w-5 h-5 text-amber-400 fill-amber-400" />
                    <span class="text-white font-medium">{{ dest.rating?.toFixed(1) || '4.5' }}</span>
                  </div>
                  <span class="text-white/80 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                    Ver más
                    <ArrowRight class="w-4 h-4" />
                  </span>
                </div>
              </div>
              <div class="absolute inset-0 bg-teal-600/0 group-hover:bg-teal-600/10 transition-colors duration-500"></div>
            </NuxtLink>
          </div>

          <div v-if="!landingData?.destinations?.length" class="text-center py-16 bg-gray-50 rounded-2xl">
            <p class="text-gray-600 mb-4">No hay destinos destacados</p>
            <NuxtLink to="/destinos" class="text-teal-600 hover:underline font-medium">Explorar todos los destinos →</NuxtLink>
          </div>

          <div class="text-center mt-12">
            <NuxtLink to="/destinos" class="inline-flex items-center gap-2 px-8 py-4 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 active:bg-teal-800 transition-all shadow-lg hover:shadow-xl">
              <span>Ver todos los destinos</span>
              <ArrowRight class="w-5 h-5" />
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- Hotels Section -->
      <section class="py-24 bg-gray-50">
        <div class="container mx-auto px-4">
          <div class="text-center mb-16">
            <span class="inline-block px-4 py-1.5 bg-amber-100 text-amber-700 text-sm font-semibold rounded-full mb-4">Alojamientos</span>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Hoteles Recomendados
            </h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Alojamientos de primera categoría para tu estancia perfecta
            </p>
          </div>
          
          <div class="grid md:grid-cols-3 gap-8">
            <NuxtLink 
              v-for="prop in landingData?.properties" 
              :key="prop.id" 
              :to="`/hoteles/${prop.slug}`" 
              class="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer"
            >
              <div class="relative h-56 overflow-hidden">
                <NuxtImg 
                  :src="prop.cover_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80'" 
                  :alt="prop.name"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  width="800"
                  height="400"
                  format="webp"
                  :placeholder="true"
                />
                <div class="absolute top-4 right-4">
                  <span class="px-4 py-1.5 bg-teal-600 text-white text-xs font-bold rounded-full uppercase tracking-wide">
                    {{ prop.property_type || 'Hotel' }}
                  </span>
                </div>
                <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </div>
              <div class="p-6">
                <h3 class="font-bold text-gray-900 text-xl mb-2 group-hover:text-teal-600 transition-colors">
                  {{ prop.name }}
                </h3>
                <p class="text-gray-600 text-sm mb-4 flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ prop.region }}
                </p>
                <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div>
                    <span class="text-2xl font-bold text-teal-600">${{ prop.base_price || prop.price || 89 }}</span>
                    <span class="text-gray-500 text-sm">/noche</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <Star class="w-5 h-5 text-amber-400 fill-amber-400" />
                    <span class="font-semibold text-gray-700">{{ prop.rating?.toFixed(1) || '4.5' }}</span>
                  </div>
                </div>
              </div>
            </NuxtLink>
          </div>

          <div v-if="!landingData?.properties?.length" class="text-center py-16 bg-white rounded-2xl">
            <p class="text-gray-600 mb-4">No hay hoteles disponibles</p>
            <NuxtLink to="/hoteles" class="text-teal-600 hover:underline font-medium">Ver todos los hoteles →</NuxtLink>
          </div>

          <div class="text-center mt-12">
            <NuxtLink to="/hoteles" class="inline-flex items-center gap-2 px-8 py-4 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 active:bg-teal-800 transition-all shadow-lg hover:shadow-xl">
              <span>Ver todos los hoteles</span>
              <ArrowRight class="w-5 h-5" />
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- Tours Section -->
      <section class="py-24 bg-white">
        <div class="container mx-auto px-4">
          <div class="text-center mb-16">
            <span class="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-700 text-sm font-semibold rounded-full mb-4">Experiencias</span>
            <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Tours y Experiencias
            </h2>
            <p class="text-xl text-gray-600 max-w-2xl mx-auto">
              Vive aventuras inolvidables con nuestros tours mejor valorados
            </p>
          </div>
          
          <div class="grid md:grid-cols-3 gap-8">
            <NuxtLink 
              v-for="tour in landingData?.tours" 
              :key="tour.id" 
              :to="`/tours/${tour.slug}`" 
              class="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer border border-gray-100"
            >
              <div class="relative h-56 overflow-hidden">
                <NuxtImg 
                  :src="tour.cover_image || 'https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800&q=80'" 
                  :alt="tour.name"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  width="800"
                  height="400"
                  format="webp"
                  :placeholder="true"
                />
                <div class="absolute top-4 left-4">
                  <span class="px-4 py-1.5 bg-amber-500 text-white text-xs font-bold rounded-full uppercase tracking-wide">
                    {{ tour.category || 'Tour' }}
                  </span>
                </div>
              </div>
              <div class="p-6">
                <h3 class="font-bold text-gray-900 text-xl mb-2 group-hover:text-teal-600 transition-colors">
                  {{ tour.name }}
                </h3>
                <p class="text-gray-600 text-sm mb-4 flex items-center gap-1">
                  <MapPin class="w-4 h-4" />
                  {{ tour.location }}
                </p>
                <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                  <div>
                    <span class="text-2xl font-bold text-teal-600">${{ tour.price || 65 }}</span>
                    <span class="text-gray-500 text-sm">/persona</span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="flex items-center gap-1">
                      <Star class="w-5 h-5 text-amber-400 fill-amber-400" />
                      <span class="font-semibold text-gray-700">{{ tour.rating?.toFixed(1) || '4.7' }}</span>
                    </div>
                    <span class="text-gray-600 text-sm flex items-center gap-1">
                      <Clock class="w-4 h-4" />
                      {{ tour.duration_text || (tour.duration_hours ? tour.duration_hours + 'h' : '4h') }}
                    </span>
                  </div>
                </div>
              </div>
            </NuxtLink>
          </div>

          <div v-if="!landingData?.tours?.length" class="text-center py-16 bg-gray-50 rounded-2xl">
            <p class="text-gray-600 mb-4">No hay tours disponibles</p>
            <NuxtLink to="/tours" class="text-teal-600 hover:underline font-medium">Ver todos los tours →</NuxtLink>
          </div>

          <div class="text-center mt-12">
            <NuxtLink to="/tours" class="inline-flex items-center gap-2 px-8 py-4 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 active:bg-teal-800 transition-all shadow-lg hover:shadow-xl">
              <span>Ver todos los tours</span>
              <ArrowRight class="w-5 h-5" />
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- Why Costa Rica -->
      <section class="py-24 bg-gradient-to-br from-teal-800 via-teal-700 to-emerald-800 relative overflow-hidden">
        <div class="absolute inset-0">
          <div class="absolute top-0 left-1/4 w-96 h-96 bg-teal-400/10 rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-emerald-400/10 rounded-full blur-3xl"></div>
        </div>
        <div class="container mx-auto px-4 relative z-10">
          <div class="text-center mb-16">
            <span class="inline-block px-4 py-1.5 bg-white/10 text-white text-sm font-semibold rounded-full mb-4 backdrop-blur-sm border border-white/20">
              ¿Por qué Costa Rica?
            </span>
            <h2 class="text-4xl md:text-5xl font-bold text-white mb-4">
              Un destino único
            </h2>
            <p class="text-xl text-white/80 max-w-2xl mx-auto">
              Tu próxima aventura te espera con brazos abiertos
            </p>
          </div>
          
          <div class="grid md:grid-cols-4 gap-8">
            <div class="text-center group">
              <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 text-4xl group-hover:bg-white/20 transition-colors border border-white/10">
                🌋
              </div>
              <h3 class="text-white font-bold text-xl mb-3">Biodiversidad</h3>
              <p class="text-white/70 text-base leading-relaxed">4% de la biodiversidad mundial en un país del tamaño de Dinamarca</p>
            </div>
            <div class="text-center group">
              <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 text-4xl group-hover:bg-white/20 transition-colors border border-white/10">
                ☀️
              </div>
              <h3 class="text-white font-bold text-xl mb-3">Clima Perfecto</h3>
              <p class="text-white/70 text-base leading-relaxed">Temperaturas entre 20-30°C todo el año, sin invierno</p>
            </div>
            <div class="text-center group">
              <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 text-4xl group-hover:bg-white/20 transition-colors border border-white/10">
                🛡️
              </div>
              <h3 class="text-white font-bold text-xl mb-3">Seguridad</h3>
              <p class="text-white/70 text-base leading-relaxed">Uno de los países más seguros de Latinoamérica</p>
            </div>
            <div class="text-center group">
              <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 text-4xl group-hover:bg-white/20 transition-colors border border-white/10">
                🌿
              </div>
              <h3 class="text-white font-bold text-xl mb-3">Ecoturismo</h3>
              <p class="text-white/70 text-base leading-relaxed">País pionero en ecoturismo con más de 30 parques nacionales</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Testimonials -->
      <TestimonialsSection />

      <!-- Featured Packages -->
      <FeaturedPackages />

      <!-- CTA Section -->
      <section class="py-24 bg-gray-900 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-gray-900 via-teal-900/20 to-gray-900"></div>
        <div class="container mx-auto px-4 relative z-10 text-center">
          <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
            ¿Listo para tu aventura?
          </h2>
          <p class="text-xl text-gray-600 mb-10 max-w-xl mx-auto">
            Crea una cuenta para planificar tu viaje, guardar favoritos y obtener ofertas exclusivas.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <NuxtLink to="/register" class="inline-flex items-center gap-2 px-10 py-5 bg-teal-600 text-white font-bold rounded-xl hover:bg-teal-700 active:bg-teal-800 transition-all shadow-lg hover:shadow-xl text-lg">
              <span>Crear Cuenta Gratis</span>
              <ArrowRight class="w-5 h-5" />
            </NuxtLink>
            <NuxtLink to="/planificador" class="inline-flex items-center gap-2 px-10 py-5 bg-white text-gray-900 font-bold rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-all text-lg border-2 border-transparent hover:border-gray-200">
              <MapPin class="w-5 h-5" />
              <span>Planificar Mi Viaje</span>
            </NuxtLink>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { 
  Search, 
  MapPin, 
  Mountain, 
  Building2, 
  Compass, 
  FileText, 
  Star, 
  ArrowRight, 
  Clock 
} from 'lucide-vue-next'

// Components
import TrustLogos from '~/components/TrustLogos.vue'
import TestimonialsSection from '~/components/TestimonialsSection.vue'
import FeaturedPackages from '~/components/FeaturedPackages.vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const search = reactive({
  destino: '',
  checkin: '',
  checkout: ''
})

const buscar = () => {
  const params = new URLSearchParams()
  if (search.destino) params.set('q', search.destino)
  if (search.checkin) params.set('checkin', search.checkin)
  if (search.checkout) params.set('checkout', search.checkout)
  navigateTo(`/search?${params.toString()}`)
}

const { data: landingData, pending, error } = useFetch(
  () => `${apiBase}/landing/content`,
  {
    key: 'landing-content',
    default: () => null
  }
)
</script>