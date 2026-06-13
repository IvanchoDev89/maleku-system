<template>
  <div class="map-page">
    <!-- Header -->
    <header class="map-header">
      <div class="header-content">
        <NuxtLink to="/" class="logo">
          <span class="logo-icon">🌴</span>
          <span class="logo-text">Costa Rica Travel</span>
        </NuxtLink>

        <div class="search-bar">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar hoteles, tours, destinos..."
            @keyup.enter="performSearch"
          />
          <button @click="performSearch">
            <span>🔍</span>
          </button>
        </div>

        <nav class="header-nav">
          <NuxtLink to="/">Inicio</NuxtLink>
          <NuxtLink to="/map">Mapa</NuxtLink>
          <NuxtLink to="/destinos">Destinos</NuxtLink>
        </nav>
      </div>
    </header>

    <!-- Main Content -->
    <div class="map-container">
      <!-- Sidebar Filters -->
      <aside class="filters-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="filters-header">
          <h2>🔍 Filtros</h2>
          <button @click="sidebarCollapsed = !sidebarCollapsed" class="toggle-btn">
            {{ sidebarCollapsed ? '→' : '←' }}
          </button>
        </div>

        <div v-if="!sidebarCollapsed" class="filters-content">
          <!-- Type Filter -->
          <div class="filter-section">
            <h3>Tipo</h3>
            <div class="filter-options">
              <label class="filter-option" :class="{ active: filters.type === 'all' }">
                <input type="radio" v-model="filters.type" value="all" />
                <span>🌍 Todo</span>
              </label>
              <label class="filter-option" :class="{ active: filters.type === 'property' }">
                <input type="radio" v-model="filters.type" value="property" />
                <span>🏨 Alojamientos</span>
              </label>
              <label class="filter-option" :class="{ active: filters.type === 'tour' }">
                <input type="radio" v-model="filters.type" value="tour" />
                <span>🧗 Tours</span>
              </label>
            </div>
          </div>

          <!-- Property Type -->
          <div v-if="filters.type === 'property' || filters.type === 'all'" class="filter-section">
            <h3>Tipo de Alojamiento</h3>
            <div class="filter-chips">
              <button
                v-for="type in propertyTypes"
                :key="type.value"
                :class="{ active: filters.propertyType === type.value }"
                @click="filters.propertyType = filters.propertyType === type.value ? '' : type.value"
              >
                {{ type.icon }} {{ type.label }}
              </button>
            </div>
          </div>

          <!-- Region Filter -->
          <div class="filter-section">
            <h3>Región</h3>
            <UiSelect v-model="filters.region" :options="regionOptions" placeholder="Todas las regiones" />
          </div>

          <!-- Price Range -->
          <div class="filter-section">
            <h3>Precio por noche</h3>
            <div class="price-inputs">
              <input v-model.number="filters.minPrice" type="number" placeholder="Min" />
              <span>-</span>
              <input v-model.number="filters.maxPrice" type="number" placeholder="Max" />
            </div>
          </div>

          <!-- Amenities -->
          <div class="filter-section">
            <h3>Amenidades</h3>
            <div class="filter-chips">
              <button
                v-for="amenity in amenityOptions"
                :key="amenity"
                :class="{ active: filters.amenities.includes(amenity) }"
                @click="toggleAmenity(amenity)"
              >
                {{ amenity }}
              </button>
            </div>
          </div>

          <!-- Apply Filters -->
          <button @click="applyFilters" class="apply-btn">
            Aplicar Filtros
          </button>

          <!-- Results Count -->
          <div class="results-count">
            <span>{{ filteredProperties.length + filteredTours.length }}</span> resultados en el mapa
          </div>
        </div>
      </aside>

      <!-- Map -->
      <div class="map-wrapper">
        <div id="map" ref="mapContainer"></div>

        <!-- Loading Overlay -->
        <div v-if="loading" class="loading-overlay">
          <div class="loader"></div>
          <p>Cargando mapa...</p>
        </div>

        <!-- Legend -->
        <div class="map-legend">
          <div class="legend-item">
            <span class="marker property-marker">🏨</span> Alojamientos
          </div>
          <div class="legend-item">
            <span class="marker tour-marker">🧗</span> Tours
          </div>
        </div>

        <!-- Zoom Controls -->
        <div class="zoom-controls">
          <button @click="zoomIn">+</button>
          <button @click="zoomOut">-</button>
          <button @click="fitBounds">⊡</button>
        </div>
      </div>
    </div>

    <!-- Property Popup (for selected property) -->
    <Transition name="slide-up">
      <div v-if="selectedItem" class="property-panel">
        <button @click="selectedItem = null" class="close-btn">×</button>

        <div class="property-content">
          <div class="property-image">
            <NuxtImg :src="selectedItem.cover_image || '/images/placeholder.jpg'" :alt="selectedItem.name" width="800" height="400" format="webp" />
            <span class="property-type-badge">
              {{ selectedItem.property_type || selectedItem.category }}
            </span>
          </div>

          <div class="property-info">
            <h3>{{ selectedItem.name }}</h3>

            <div class="property-location">
              📍 {{ selectedItem.city || selectedItem.location }}
            </div>

            <div class="property-rating" v-if="selectedItem.rating">
              ⭐ {{ selectedItem.rating.toFixed(1) }} ({{ selectedItem.total_reviews }} reseñas)
            </div>

            <div class="property-price">
              <span class="price">${{ selectedItem.base_price || selectedItem.price }}</span>
              <span class="per-night">/ noche</span>
            </div>

            <div v-if="selectedItem.amenities?.length" class="property-amenities">
              <span v-for="amenity in selectedItem.amenities.slice(0, 4)" :key="amenity" class="amenity-tag">
                {{ amenity }}
              </span>
            </div>

            <div class="property-actions">
              <NuxtLink :to="`/hoteles/${selectedItem.slug}`" class="view-btn">
                Ver Detalles →
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const router = useRouter()

const mapContainer = ref<HTMLElement | null>(null)
const loading = ref(true)
const sidebarCollapsed = ref(false)
const searchQuery = ref('')
const selectedItem = ref<any>(null)

let map: any = null
let markers: any[] = []

const properties = ref<any[]>([])
const tours = ref<any[]>([])

const filters = reactive({
  type: 'all',
  propertyType: '',
  region: '',
  minPrice: null as number | null,
  maxPrice: null as number | null,
  amenities: [] as string[]
})

const propertyTypes = [
  { value: 'hotel', label: 'Hotel', icon: '🏨' },
  { value: 'villa', label: 'Villa', icon: '🏡' },
  { value: 'resort', label: 'Resort', icon: '🏖️' },
  { value: 'apartment', label: 'Apartamento', icon: '🏢' },
  { value: 'hostel', label: 'Hostel', icon: '🛏️' },
  { value: 'eco_lodge', label: 'Eco Lodge', icon: '🌿' },
  { value: 'cabin', label: 'Cabaña', icon: '🏔️' },
  { value: 'glamping', label: 'Glamping', icon: '⛺' }
]

const amenityOptions = ['WiFi', 'Piscina', 'Parking', 'A/C', 'Desayuno', 'Playa', 'Mascotas', 'Spa']

const regions = [
  'Guanacaste',
  'Puntarenas',
  'Alajuela',
  'Cartago',
  'Heredia',
  'San José',
  'Limón'
]

const filteredProperties = computed(() => {
  return properties.value.filter(p => {
    if (filters.type === 'tour') return false
    if (filters.propertyType && p.property_type !== filters.propertyType) return false
    if (filters.region && p.region !== filters.region) return false
    if (filters.minPrice && (p.base_price || 0) < filters.minPrice) return false
    if (filters.maxPrice && (p.base_price || 0) > filters.maxPrice) return false
    return true
  })
})

const filteredTours = computed(() => {
  return tours.value.filter(t => {
    if (filters.type === 'property') return false
    if (filters.region && t.location !== filters.region) return false
    if (filters.minPrice && (t.price || 0) < filters.minPrice) return false
    if (filters.maxPrice && (t.price || 0) > filters.maxPrice) return false
    return true
  })
})

const regionOptions = [
  { value: '', label: 'Todas las regiones' },
  ...regions.map(r => ({ value: r, label: r })),
]

const toggleAmenity = (amenity: string) => {
  const idx = filters.amenities.indexOf(amenity)
  if (idx > -1) {
    filters.amenities.splice(idx, 1)
  } else {
    filters.amenities.push(amenity)
  }
}

const fetchMapData = async () => {
  loading.value = true
  try {
    const data = await api.get<any>('/search/map')
    properties.value = data.properties || []
    tours.value = data.tours || []

    await nextTick()
    initMap()
  } catch (e) {
    console.error('Error loading map data:', e)
  } finally {
    loading.value = false
  }
}

const initMap = async () => {
  if (!mapContainer.value || typeof window === 'undefined') return

  // Dynamically import Leaflet to avoid SSR issues
  const L = await import('leaflet')

  // Fix default marker icons
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png'
  })

  // Initialize map centered on Costa Rica
  map = L.map('map').setView([9.7489, -83.7534], 8)

  // Add tile layer (OpenStreetMap)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // Add markers
  updateMarkers()
}

const updateMarkers = async () => {
  if (!map) return

  const L = await import('leaflet')

  // Clear existing markers
  markers.forEach(m => map.removeLayer(m))
  markers = []

  // Add property markers
  filteredProperties.value.forEach(p => {
    if (p.latitude && p.longitude) {
      const icon = L.divIcon({
        className: 'custom-marker property-marker',
        html: `<div class="marker-pin property">🏨</div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 40]
      })

      const marker = L.marker([p.latitude, p.longitude], { icon })
        .addTo(map)
        .on('click', () => selectProperty(p))

      markers.push(marker)
    }
  })

  // Add tour markers
  filteredTours.value.forEach(t => {
    if (t.latitude && t.longitude) {
      const icon = L.divIcon({
        className: 'custom-marker tour-marker',
        html: `<div class="marker-pin tour">🧗</div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 40]
      })

      const marker = L.marker([t.latitude, t.longitude], { icon })
        .addTo(map)
        .on('click', () => selectTour(t))

      markers.push(marker)
    }
  })

  // Fit bounds if markers exist
  if (markers.length > 0) {
    const group = L.featureGroup(markers)
    map.fitBounds(group.getBounds().pad(0.1))
  }
}

const selectProperty = (property: any) => {
  selectedItem.value = property
}

const selectTour = (tour: any) => {
  selectedItem.value = tour
}

const applyFilters = () => {
  updateMarkers()
}

const performSearch = () => {
  if (searchQuery.value) {
    // Filter by search query
    const query = searchQuery.value.toLowerCase()
    properties.value = properties.value.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.city?.toLowerCase().includes(query) ||
      p.region?.toLowerCase().includes(query)
    )
    tours.value = tours.value.filter(t =>
      t.name.toLowerCase().includes(query) ||
      t.location?.toLowerCase().includes(query)
    )
    updateMarkers()
  }
}

const zoomIn = () => map?.zoomIn()
const zoomOut = () => map?.zoomOut()
const fitBounds = () => {
  if (markers.length > 0) {
    import('leaflet').then(L => {
      const group = L.featureGroup(markers)
      map.fitBounds(group.getBounds().pad(0.1))
    })
  }
}

onMounted(() => {
  fetchMapData()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch([filteredProperties, filteredTours], () => {
  updateMarkers()
})
</script>

<style>
/* Import Leaflet CSS */
@import url('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css');

.map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.75rem 1.5rem;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 2rem;
  max-width: 1800px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1.25rem;
  color: #059669;
  text-decoration: none;
}

.search-bar {
  flex: 1;
  max-width: 500px;
  display: flex;
  gap: 0;
}

.search-bar input {
  flex: 1;
  padding: 0.625rem 1rem;
  border: 1px solid #d1d5db;
  border-right: none;
  border-radius: 0.5rem 0 0 0.5rem;
  font-size: 0.875rem;
}

.search-bar button {
  padding: 0.625rem 1rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 0 0.5rem 0.5rem 0;
}

.header-nav {
  display: flex;
  gap: 1.5rem;
}

.header-nav a {
  color: #374151;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.header-nav a:hover {
  color: #059669;
}

.map-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.filters-sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.filters-sidebar.collapsed {
  width: 48px;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.filters-header h2 {
  font-size: 1rem;
  font-weight: 600;
}

.toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  color: #6b7280;
}

.filters-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-section h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #374151;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-option.active {
  background: #ecfdf5;
  color: #059669;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-chips button {
  padding: 0.375rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 9999px;
  font-size: 0.75rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chips button.active {
  background: #059669;
  color: white;
  border-color: #059669;
}

.filter-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.price-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.price-inputs input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.apply-btn {
  width: 100%;
  padding: 0.75rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.apply-btn:hover {
  background: #047857;
}

.results-count {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.results-count span {
  font-weight: 700;
  color: #059669;
}

.map-wrapper {
  flex: 1;
  position: relative;
}

#map {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.loader {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top-color: #059669;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.map-legend {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  background: white;
  padding: 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  gap: 1rem;
  z-index: 500;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.marker-pin {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  font-size: 1rem;
}

.marker-pin.property {
  background: #059669;
}

.marker-pin.tour {
  background: #f59e0b;
}

.zoom-controls {
  position: absolute;
  right: 1rem;
  bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  z-index: 500;
}

.zoom-controls button {
  width: 36px;
  height: 36px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.zoom-controls button:hover {
  background: #f3f4f6;
}

.property-panel {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 600px;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  z-index: 1000;
  overflow: hidden;
}

.close-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 28px;
  height: 28px;
  background: rgba(0,0,0,0.5);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 1.25rem;
  cursor: pointer;
  z-index: 10;
}

.property-content {
  display: flex;
  gap: 1rem;
}

.property-image {
  width: 200px;
  position: relative;
  flex-shrink: 0;
}

.property-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.property-type-badge {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  text-transform: capitalize;
}

.property-info {
  flex: 1;
  padding: 1rem 1rem 1rem 0;
}

.property-info h3 {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.property-location {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.property-rating {
  color: #f59e0b;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.property-price {
  margin-bottom: 0.75rem;
}

.property-price .price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #059669;
}

.property-price .per-night {
  color: #6b7280;
  font-size: 0.875rem;
}

.property-amenities {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.amenity-tag {
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.625rem;
  color: #4b5563;
}

.view-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #059669;
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.view-btn:hover {
  background: #047857;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

/* Custom marker styles */
.custom-marker {
  background: transparent !important;
  border: none !important;
}

.leaflet-container {
  font-family: inherit;
}
</style>
