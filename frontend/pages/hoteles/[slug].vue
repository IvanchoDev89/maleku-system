<script setup lang="ts">
import type { Property, Room, CalendarDay } from '~/types'
import {
  MapPin, Star, Phone, Mail, AlertCircle, Check, Clock, Users,
  ChevronLeft, ChevronRight, Info, Wifi, Coffee, Car, Snowflake,
  Waves, Dumbbell, Utensils, GlassWater, Dog, Shirt, Headphones,
  ShieldCheck, Accessibility, Calendar, CreditCard
} from 'lucide-vue-next'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const router = useRouter()
const slug = route.params.slug as string
const api = useApi()

// === State ===
const property = ref<Property | null>(null)
const pending = ref(true)
const error = ref('')
const selectedRoom = ref<Room | null>(null)
const checkIn = ref<string | null>(null)
const checkOut = ref<string | null>(null)
const guests = ref(2)
const nights = ref(0)
const checkingAvailability = ref(false)
const availabilityResult = ref<{ available: boolean; message?: string } | null>(null)
const pricePreview = ref<any>(null)
const loadingPrice = ref(false)
const activeImageIndex = ref(0)

// === Fetch Property ===
const { data: propertyData, pending: loading, error: fetchError } = await useFetch<Property>(
  () => `${apiBase}/properties/slug/${slug}`,
  { default: () => null, key: slug }
)
property.value = propertyData.value

const guestOptions = computed(() => {
  if (!property.value) return []
  const max = property.value.max_guests || 10
  const arr = []
  for (let i = 1; i <= max; i++) {
    arr.push({ value: String(i), label: `${i} ${i === 1 ? 'huésped' : 'huéspedes'}` })
  }
  return arr
})

// === Room Selection ===
const selectRoom = (room: Room) => {
  selectedRoom.value = room
  checkIn.value = null
  checkOut.value = null
  nights.value = 0
  availabilityResult.value = null
  pricePreview.value = null
}

const roomChanged = () => {
  checkIn.value = null
  checkOut.value = null
  nights.value = 0
  availabilityResult.value = null
  pricePreview.value = null
}

// === Availability Check ===
const checkAvailability = async () => {
  if (!selectedRoom.value || !checkIn.value) return
  checkingAvailability.value = true
  availabilityResult.value = null
  pricePreview.value = null
  try {
    const checkOutDate = checkOut.value || checkIn.value
    const result = await api.post<{ available: boolean; alternative_dates: any[] }>(
      '/availability/rooms/check',
      {
        room_id: selectedRoom.value.id,
        check_in: checkIn.value + 'T14:00:00Z',
        check_out: checkOutDate + 'T12:00:00Z',
      }
    )
    availabilityResult.value = { available: result.available }

    if (result.available && checkOut.value) {
      await loadPricePreview()
    }
  } catch (e: any) {
    availabilityResult.value = {
      available: false,
      message: e?.data?.detail || 'Error al verificar disponibilidad'
    }
  } finally {
    checkingAvailability.value = false
  }
}

const loadPricePreview = async () => {
  if (!selectedRoom.value || !checkIn.value || !checkOut.value) return
  loadingPrice.value = true
  try {
    const result = await api.post<any>('/bookings/preview', {
      room_id: selectedRoom.value.id,
      check_in: checkIn.value + 'T14:00:00Z',
      check_out: checkOut.value + 'T12:00:00Z',
      guests: guests.value,
    })
    pricePreview.value = result
  } catch {
    pricePreview.value = null
  } finally {
    loadingPrice.value = false
  }
}

watch([checkIn, checkOut, guests], async () => {
  if (checkIn.value && checkOut.value && selectedRoom.value) {
    await checkAvailability()
  } else {
    availabilityResult.value = null
    pricePreview.value = null
  }
})

// === Booking ===
const goToCheckout = () => {
  if (!selectedRoom.value || !checkIn.value || !checkOut.value || !property.value) return
  const params = new URLSearchParams({
    roomId: selectedRoom.value.id,
    propertyId: property.value.id,
    checkIn: checkIn.value,
    checkOut: checkOut.value,
    guests: String(guests.value),
    total: String(pricePreview.value?.total || 0),
    experience: property.value.name,
    roomName: selectedRoom.value.name,
  })
  router.push(`/checkout?${params.toString()}`)
}

// === Display Helpers ===
const formatPropertyType = (type: string | undefined) => {
  const types: Record<string, string> = {
    hotel: 'Hotel', resort: 'Resort', villa: 'Villa',
    boutique: 'Boutique', eco_lodge: 'Eco Lodge', hostel: 'Hostel',
    apartment: 'Apartamento', cabin: 'Cabaña', glamping: 'Glamping',
    aparthotel: 'Apartotel',
  }
  return types[type || ''] || type || 'Hotel'
}

const amenityIcon = (amenity: string) => {
  const icons: Record<string, string> = {
    wifi: '📶', pool: '🏊', parking: '🅿️', ac: '❄️',
    restaurant: '🍽️', bar: '🍸', spa: '💆', gym: '🏋️',
    beach: '🏖️', pets: '🐕', breakfast: '🍳', room_service: '🛎️',
    laundry: '👕', concierge: '🎩', security: '🔒', accessibility: '♿',
  }
  return icons[amenity.toLowerCase()] || '✓'
}

const allImages = computed(() => {
  const p = property.value
  if (!p) return []
  const images: string[] = []
  if (p.cover_image) images.push(p.cover_image)
  if (p.images?.length) {
    p.images.forEach(img => {
      if (img !== p.cover_image) images.push(img)
    })
  }
  return images.length ? images : ['https://images.unsplash.com/photo-1566073771259-6a8506099945']
})

const goToPrevImage = () => {
  activeImageIndex.value = activeImageIndex.value === 0
    ? allImages.value.length - 1
    : activeImageIndex.value - 1
}

const goToNextImage = () => {
  activeImageIndex.value = activeImageIndex.value === allImages.value.length - 1
    ? 0
    : activeImageIndex.value + 1
}

const isBookable = computed(() => {
  return selectedRoom.value && checkIn.value && checkOut.value
    && availabilityResult.value?.available
})

useSeo({
  title: computed(() => property.value?.name
    ? `${property.value.name} | Costa Rica Travel` : 'Hotel'),
  description: computed(() => property.value?.short_description || ''),
  ogType: 'website',
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="container">
      <!-- Loading Skeleton -->
      <div v-if="loading" class="space-y-8">
        <div class="h-8 w-48 bg-gray-200 animate-pulse rounded"></div>
        <div class="grid grid-cols-4 gap-2">
          <div class="col-span-2 row-span-2 h-96 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
          <div class="h-48 bg-gray-200 animate-pulse rounded"></div>
        </div>
      </div>

      <div v-else-if="fetchError">
        <div class="text-center py-16">
          <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle class="w-12 h-12 text-red-400" />
          </div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Error al cargar la propiedad</h3>
          <p class="text-gray-600 mb-6">Por favor intenta de nuevo más tarde.</p>
          <NuxtLink to="/hoteles" class="px-6 py-3 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 inline-block">
            Volver a hoteles
          </NuxtLink>
        </div>
      </div>

      <template v-else-if="property">
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

        <!-- Image Gallery -->
        <div class="relative rounded-2xl overflow-hidden mb-8 group">
          <div class="aspect-[21/9] relative">
            <NuxtImg
              :src="allImages[activeImageIndex]"
              :alt="property.name"
              class="w-full h-full object-cover"
              width="1200"
              height="600"
              format="webp"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
          </div>
          <button
            v-if="allImages.length > 1"
            @click="goToPrevImage"
            title="Imagen anterior"
            class="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors opacity-0 group-hover:opacity-100"
          >
            <ChevronLeft class="w-5 h-5 text-gray-700" />
          </button>
          <button
            v-if="allImages.length > 1"
            @click="goToNextImage"
            title="Imagen siguiente"
            class="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors opacity-0 group-hover:opacity-100"
          >
            <ChevronRight class="w-5 h-5 text-gray-700" />
          </button>
          <div
            v-if="allImages.length > 1"
            class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2"
          >
            <button
              v-for="(_, idx) in allImages"
              :key="idx"
              @click="activeImageIndex = idx"
              class="w-2.5 h-2.5 rounded-full transition-colors"
              :class="idx === activeImageIndex ? 'bg-white' : 'bg-white/50'"
            />
          </div>
        </div>

        <!-- Main Content -->
        <div class="grid lg:grid-cols-3 gap-12">
          <!-- Left: Details -->
          <div class="lg:col-span-2 space-y-10">
            <!-- Header -->
            <div>
              <div class="flex items-center gap-3 mb-3">
                <span class="inline-block px-3 py-1 bg-primary-100 text-primary-700 text-sm font-semibold rounded-full">
                  {{ formatPropertyType(property.property_type) }}
                </span>
                <span v-if="property.is_featured" class="inline-block px-3 py-1 bg-amber-100 text-amber-700 text-sm font-semibold rounded-full">
                  Destacado
                </span>
              </div>
              <h1 class="text-4xl font-bold text-gray-900">{{ property.name }}</h1>
              <div class="flex items-center gap-4 mt-3 flex-wrap">
                <div class="flex items-center gap-1">
                  <Star class="w-5 h-5 text-amber-400 fill-amber-400" />
                  <span class="font-bold text-gray-900">{{ property.rating?.toFixed(1) || '—' }}</span>
                  <span class="text-gray-500">({{ property.total_reviews || 0 }} reseñas)</span>
                </div>
                <span class="text-gray-300">|</span>
                <span class="text-gray-600 flex items-center gap-1.5">
                  <MapPin class="w-4 h-4 text-gray-400" />
                  {{ property.city }}{{ property.province ? ', ' + property.province : '' }}
                </span>
                <span v-if="property.vendor" class="text-gray-600 text-sm">
                  Vendido por <span class="font-medium">{{ property.vendor.business_name }}</span>
                </span>
              </div>
            </div>

            <!-- Description -->
            <section>
              <p class="text-gray-600 leading-relaxed text-lg">{{ property.short_description }}</p>
              <p v-if="property.description" class="text-gray-600 leading-relaxed mt-4">{{ property.description }}</p>
            </section>

            <!-- Amenities -->
            <section v-if="property.amenities?.length">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Servicios</h2>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <div
                  v-for="amenity in property.amenities"
                  :key="amenity"
                  class="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-100"
                >
                  <span class="text-lg">{{ amenityIcon(amenity) }}</span>
                  <span class="text-gray-700 text-sm capitalize">{{ amenity.replace(/_/g, ' ') }}</span>
                </div>
              </div>
            </section>

            <!-- Rooms -->
            <section v-if="property.rooms?.length">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Habitaciones</h2>
              <div class="space-y-4">
                <div
                  v-for="room in property.rooms"
                  :key="room.id"
                  @click="selectRoom(room)"
                  class="bg-white rounded-xl border-2 p-5 cursor-pointer transition-all hover:shadow-md"
                  :class="selectedRoom?.id === room.id ? 'border-primary-500 shadow-md' : 'border-gray-100'"
                >
                  <div class="flex justify-between items-start">
                    <div>
                      <h3 class="font-semibold text-gray-900 text-lg">{{ room.name }}</h3>
                      <p v-if="room.description" class="text-gray-500 text-sm mt-1">{{ room.description }}</p>
                      <div class="flex items-center gap-4 mt-2 text-sm text-gray-500">
                        <span class="flex items-center gap-1">
                          <Users class="w-4 h-4" />
                          Hasta {{ room.max_guests }} huéspedes
                        </span>
                        <span>{{ room.beds }} cama{{ room.beds > 1 ? 's' : '' }}</span>
                        <span v-if="room.bed_type">{{ room.bed_type }}</span>
                      </div>
                    </div>
                    <div class="text-right">
                      <p class="text-2xl font-bold text-primary-600">${{ room.price_per_night }}</p>
                      <p class="text-sm text-gray-500">/noche</p>
                    </div>
                  </div>
                  <div v-if="room.extra_guest_price > 0" class="mt-2 text-xs text-gray-400">
                    Huésped extra: ${{ room.extra_guest_price }}/noche
                  </div>
                </div>
              </div>
            </section>

            <!-- Policies -->
            <section v-if="property.cancellation_policy || property.check_in_time || property.check_out_time">
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Políticas</h2>
              <div class="bg-white rounded-xl border border-gray-100 p-6 space-y-4">
                <div v-if="property.check_in_time" class="flex items-center gap-3">
                  <Clock class="w-5 h-5 text-primary-600" />
                  <div>
                    <p class="font-medium text-gray-900">Check-in</p>
                    <p class="text-gray-500">A partir de las {{ property.check_in_time }}</p>
                  </div>
                </div>
                <div v-if="property.check_out_time" class="flex items-center gap-3">
                  <Clock class="w-5 h-5 text-primary-600" />
                  <div>
                    <p class="font-medium text-gray-900">Check-out</p>
                    <p class="text-gray-500">Antes de las {{ property.check_out_time }}</p>
                  </div>
                </div>
                <div v-if="property.cancellation_policy" class="flex items-start gap-3">
                  <Info class="w-5 h-5 text-primary-600 mt-0.5" />
                  <div>
                    <p class="font-medium text-gray-900">Cancelación</p>
                    <p class="text-gray-500">{{ property.cancellation_policy }}</p>
                  </div>
                </div>
              </div>
            </section>

            <!-- Location -->
            <section>
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Ubicación</h2>
              <div class="aspect-video bg-gray-200 rounded-xl flex items-center justify-center">
                <div class="text-center p-8">
                  <MapPin class="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p class="text-gray-600 font-medium">{{ property.city }}{{ property.province ? ', ' + property.province : '' }}</p>
                  <p v-if="property.address" class="text-gray-500 text-sm mt-1">{{ property.address }}</p>
                  <p class="text-gray-400 text-sm mt-1">{{ property.country }}</p>
                </div>
              </div>
            </section>
          </div>

          <!-- Right: Booking Sidebar -->
          <div>
            <div class="sticky top-24 space-y-6">
              <!-- Booking Card -->
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div class="flex justify-between items-end mb-6">
                  <div>
                    <span class="text-4xl font-bold text-primary-600">
                      ${{ selectedRoom?.price_per_night || property.base_price }}
                    </span>
                    <span class="text-gray-500">/noche</span>
                  </div>
                  <div class="text-right text-sm">
                    <span class="text-green-600 font-medium">Excelente</span>
                    <p class="text-gray-500">{{ property.rating?.toFixed(1) || '—' }} de 5</p>
                  </div>
                </div>

                <!-- Room Selection -->
                <div v-if="property.rooms?.length > 0" class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Tipo de habitación</label>
                  <select
                    v-model="selectedRoom"
                    @change="roomChanged"
                    class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
                  >
                    <option :value="null" disabled>Seleccionar habitación</option>
                    <option
                      v-for="room in property.rooms"
                      :key="room.id"
                      :value="room"
                    >
                      {{ room.name }} - ${{ room.price_per_night }}/noche
                    </option>
                  </select>
                </div>

                <!-- Calendar -->
                <div v-if="selectedRoom" class="mb-4">
                  <AvailabilityCalendar
                    :room-id="selectedRoom.id"
                    :check-in="checkIn"
                    :check-out="checkOut"
                    :price-per-night="selectedRoom.price_per_night"
                    @update:check-in="(v) => { checkIn = v; availabilityResult = null; pricePreview = null }"
                    @update:check-out="(v) => { checkOut = v; availabilityResult = null; pricePreview = null }"
                    @nights-changed="(n) => nights = n"
                  />
                </div>

                <!-- Guests -->
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Huéspedes</label>
                  <select
                    v-model="guests"
                    class="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white"
                  >
                    <option
                      v-for="opt in guestOptions"
                      :key="opt.value"
                      :value="Number(opt.value)"
                    >
                      {{ opt.label }}
                    </option>
                  </select>
                </div>

                <!-- Checking Availability -->
                <div v-if="checkingAvailability" class="text-center py-2 text-sm text-gray-500">
                  Verificando disponibilidad...
                </div>

                <!-- Availability Result -->
                <div
                  v-else-if="availabilityResult && !availabilityResult.available"
                  class="p-3 bg-red-50 border border-red-100 rounded-xl text-sm text-red-700 mb-4 flex items-center gap-2"
                >
                  <AlertCircle class="w-4 h-4 flex-shrink-0" />
                  {{ availabilityResult.message || 'No disponible para estas fechas' }}
                </div>

                <!-- Price Preview -->
                <div v-if="pricePreview && availabilityResult?.available" class="mb-4 p-4 bg-green-50 rounded-xl">
                  <div class="flex items-center gap-2 text-green-700 font-medium mb-2">
                    <Check class="w-4 h-4" />
                    <span>Disponible</span>
                  </div>
                  <div class="space-y-1 text-sm">
                    <div class="flex justify-between text-gray-600">
                      <span>{{ pricePreview.nights }} noches x ${{ pricePreview.weekday_price }}/noche</span>
                      <span>${{ pricePreview.weekday_total }}</span>
                    </div>
                    <div v-if="pricePreview.weekend_nights > 0" class="flex justify-between text-gray-600">
                      <span>{{ pricePreview.weekend_nights }} fines de semana x ${{ pricePreview.weekend_price }}/noche</span>
                      <span>${{ pricePreview.weekend_total }}</span>
                    </div>
                    <div v-if="pricePreview.extra_guests > 0" class="flex justify-between text-gray-600">
                      <span>{{ pricePreview.extra_guests }} huésped(es) extra x ${{ pricePreview.extra_guest_price }}</span>
                      <span>${{ pricePreview.extra_guests_total }}</span>
                    </div>
                    <div v-if="pricePreview.weekly_discount_percent > 0" class="flex justify-between text-green-600">
                      <span>Descuento semanal ({{ pricePreview.weekly_discount_percent }}%)</span>
                      <span>-${{ pricePreview.weekly_discount_amount }}</span>
                    </div>
                    <div class="flex justify-between font-bold text-gray-900 pt-2 border-t border-green-200 mt-2">
                      <span>Total</span>
                      <span>${{ pricePreview.total }}</span>
                    </div>
                  </div>
                </div>

                <!-- Booking Button -->
                <button
                  class="w-full py-4 bg-gradient-to-r from-primary-600 to-emerald-600 text-white font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  :disabled="!isBookable"
                  @click="goToCheckout"
                >
                  <Calendar class="w-5 h-5" />
                  Reservar Ahora
                </button>

                <p class="text-center text-gray-500 text-sm mt-4">Sin pagos inmediatos</p>
              </div>

              <!-- Contact -->
              <div class="p-4 bg-white rounded-xl border border-gray-100">
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
