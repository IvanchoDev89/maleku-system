<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Loading -->
      <div v-if="pending" class="space-y-8">
        <div class="h-8 w-48 bg-gray-200 animate-pulse rounded"></div>
        <div class="grid grid-cols-4 gap-2">
          <div class="col-span-2 row-span-2 h-96 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
        </div>
      </div>

      <div v-else-if="property">
        <!-- Error State -->
        <div v-if="error" class="text-center py-16">
          <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle class="w-12 h-12 text-red-400" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Error al cargar la propiedad</h3>
          <p class="text-gray-600 mb-6">Por favor intenta de nuevo más tarde.</p>
          <NuxtLink to="/hoteles" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-colors inline-block">
            Volver a hoteles
          </NuxtLink>
        </div>

        <template v-else>
        <!-- Breadcrumb -->
        <nav class="mb-8">
          <ol class="flex items-center gap-2 text-sm">
            <li><NuxtLink to="/" class="text-gray-500 hover:text-primary-600">Inicio</NuxtLink></li>
            <li><span class="text-gray-400">/</span></li>
            <li><NuxtLink to="/hoteles" class="text-gray-500 hover:text-primary-600">Hoteles</NuxtLink></li>
            <li><span class="text-gray-400">/</span></li>
            <li class="text-gray-900 font-medium">{{ property.name }}</li>
          </ol>
        </nav>

        <!-- Gallery -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 rounded-2xl overflow-hidden mb-8">
          <div class="col-span-2 row-span-2 relative h-80 md:h-96">
            <NuxtImg
              :src="property.cover_image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80'"
              :alt="property.name"
              class="w-full h-full object-cover"
              width="800"
              height="600"
              format="webp"
            />
          </div>
          <div class="relative h-40 md:h-48">
            <NuxtImg
              src="https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=400&q=80"
              alt="Habitación"
              class="w-full h-full object-cover"
              width="400"
              height="300"
              format="webp"
              loading="lazy"
            />
          </div>
          <div class="relative h-40 md:h-48">
            <NuxtImg
              src="https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=400&q=80"
              alt="Piscina"
              class="w-full h-full object-cover"
              width="400"
              height="300"
              format="webp"
              loading="lazy"
            />
          </div>
          <div class="relative h-40 md:h-48">
            <NuxtImg
              src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=80"
              alt="Restaurante"
              class="w-full h-full object-cover"
              width="400"
              height="300"
              format="webp"
              loading="lazy"
            />
          </div>
          <div class="relative h-40 md:h-48 bg-gray-200 flex items-center justify-center cursor-pointer hover:bg-gray-300 transition-colors">
            <span class="text-gray-600 font-medium">+ más fotos</span>
          </div>
        </div>

        <!-- Main Content -->
        <div class="grid lg:grid-cols-3 gap-12">
          <div class="lg:col-span-2">
            <!-- Header -->
            <div class="flex items-start justify-between mb-6">
              <div>
                <span class="inline-block px-3 py-1 bg-primary-100 text-primary-700 text-sm font-semibold rounded-full">
                  {{ formatPropertyType(property.property_type) }}
                </span>
                <h1 class="text-4xl font-bold text-gray-900 mt-2">{{ property.name }}</h1>
                <div class="flex items-center gap-4 mt-3">
                  <div class="flex items-center gap-1">
                    <Star class="w-5 h-5 text-amber-400 fill-amber-400" />
                    <span class="font-bold text-gray-900 text-lg">{{ property.rating?.toFixed(1) }}</span>
                    <span class="text-gray-500">({{ property.total_reviews }} reseñas)</span>
                  </div>
                  <span class="text-gray-400">•</span>
                  <span class="text-gray-600 flex items-center gap-1">
                    <MapPin class="w-4 h-4" />
                    {{ property.city }}, {{ property.region }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Description -->
            <section class="mb-8">
              <p class="text-gray-600 leading-relaxed text-lg">{{ property.short_description }}</p>
            </section>

            <!-- Amenities -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Servicios Incluidos</h2>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div 
                  v-for="(amenity, index) in getAmenities()"
                  :key="amenity"
                  class="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-100"
                >
                  <span class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 text-sm">✓</span>
                  <span class="text-gray-700">{{ amenity }}</span>
                </div>
              </div>
            </section>

            <!-- Location -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Ubicación</h2>
              <div class="aspect-video bg-gray-200 rounded-xl flex items-center justify-center">
                <div class="text-center">
                  <MapPin class="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p class="text-gray-600">{{ property.city }}, {{ property.province }}</p>
                </div>
              </div>
            </section>

            <!-- Reviews Preview -->
            <section class="mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Reseñas Destacadas</h2>
              <div class="bg-white rounded-xl p-6 border border-gray-100">
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <span class="font-bold text-primary-700">MG</span>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-900">María García</p>
                    <p class="text-sm text-gray-500">Febrero 2026</p>
                  </div>
                  <div class="ml-auto flex items-center gap-1">
                    <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                    <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                    <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                    <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                    <Star class="w-4 h-4 text-amber-400 fill-amber-400" />
                  </div>
                </div>
                <p class="text-gray-600">"Increíble experiencia. Las instalaciones son de primera y el personal muy atento. Definitivamente volveremos."</p>
              </div>
            </section>
          </div>

          <!-- Sidebar - Booking -->
          <div>
            <div class="sticky top-24">
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div class="flex justify-between items-end mb-6">
                  <div>
                    <span class="text-4xl font-bold text-primary-600">${{ property.base_price }}</span>
                    <span class="text-gray-500">/noche</span>
                  </div>
                  <div class="text-right text-sm">
                    <span class="text-green-600 font-medium">Excelente</span>
                    <p class="text-gray-500">{{ property.rating?.toFixed(1) }} de 5</p>
                  </div>
                </div>

                <div class="space-y-4 mb-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Check-in</label>
                    <input 
                      v-model="checkin" 
                      type="date" 
                      class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Check-out</label>
                    <input 
                      v-model="checkout" 
                      type="date" 
                      class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Huéspedes</label>
                    <UiSelect v-model="guests" :options="guestOptions" />
                  </div>
                </div>

                <button class="w-full py-4 bg-gradient-to-r from-primary-600 to-emerald-600 text-white font-bold rounded-xl hover:shadow-lg transition-all">
                  Reservar Ahora
                </button>

                <p class="text-center text-gray-500 text-sm mt-4">Sin pagos inmediatos</p>
              </div>

              <!-- Contact -->
              <div class="mt-6 p-4 bg-white rounded-xl border border-gray-100">
                <h3 class="font-semibold text-gray-900 mb-2">¿Necesitas ayuda?</h3>
                <p class="text-gray-600 text-sm mb-4">Contáctanos directamente</p>
                <div class="space-y-2">
                  <a href="tel:+50688888888" class="flex items-center gap-2 text-primary-600 hover:text-primary-700">
                    <Phone class="w-4 h-4" />
                    +506 8888 8888
                  </a>
                  <a href="mailto:info@costaricatravel.dev" class="flex items-center gap-2 text-primary-600 hover:text-primary-700">
                    <Mail class="w-4 h-4" />
                    info@costaricatravel.dev
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
        </template>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-16">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">Hotel no encontrado</h1>
        <p class="text-gray-600 mb-6">El hotel que buscas no existe o ha sido eliminado.</p>
        <NuxtLink to="/hoteles" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700">
          Ver todos los hoteles
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MapPin, Star, Phone, Mail } from 'lucide-vue-next'

const guests = ref('2')

const guestOptions = [
  { value: '1', label: '1 huésped' },
  { value: '2', label: '2 huéspedes' },
  { value: '3', label: '3 huéspedes' },
  { value: '4', label: '4 huéspedes' },
]

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const slug = route.params.slug

const checkin = ref('')
const checkout = ref('')

const { data: property, pending, error } = useFetch(
  () => `${apiBase}/properties/${slug}`,
  {
    default: () => null
  }
)

const formatPropertyType = (type: string | undefined) => {
  const types: Record<string, string> = {
    hotel: 'Hotel',
    resort: 'Resort',
    villa: 'Villa',
    boutique: 'Boutique',
    eco_lodge: 'Eco Lodge'
  }
  return types[type || ''] || type || 'Hotel'
}

const getAmenities = () => {
  const type = property.value?.property_type
  const defaultAmenities: Record<string, string[]> = {
    resort: ['Piscina', 'Spa', 'Restaurante', 'Bar', 'Wifi', 'Parking', 'Gimnasio', 'A/C', 'Room Service', 'Playas'],
    hotel: ['Wifi', 'Parking', 'Restaurante', 'A/C', 'Recepción 24h', 'Room Service'],
    eco_lodge: ['Wifi', 'Desayuno', 'Tours', 'Guía Naturalista', 'Senderismo'],
    villa: ['Piscina', 'Cocina', 'A/C', 'Wifi', 'Parking', 'Vista al mar'],
    boutique: ['Wifi', 'Restaurante', 'Bar', 'Spa', 'A/C']
  }
  return defaultAmenities[type || 'hotel'] || defaultAmenities.hotel
}

useSeo({
  title: computed(() => property.value?.name ? `${property.value.name} | Costa Rica Travel` : 'Hotel'),
  description: computed(() => property.value?.short_description || ''),
  ogType: 'website'
})
</script>