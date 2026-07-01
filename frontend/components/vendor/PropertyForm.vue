<template>
  <div>
    <!-- Tabs Navigation -->
    <div class="bg-white rounded-xl shadow-sm mb-6">
      <div class="border-b overflow-x-auto">
        <nav class="flex gap-1 px-4">
          <button
            v-for="(tab, index) in tabs"
            :key="tab.id"
            @click="activeTab = index"
            class="px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap"
            :class="activeTab === index ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            <span class="flex items-center gap-2">
              <span class="text-lg">{{ tab.icon }}</span>
              {{ tab.label }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <!-- Info -->
        <div v-show="activeTab === 0" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de la Propiedad *</label>
              <input v-model="form.name" type="text" required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="Hotel Paradise Beach Resort" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Slug (URL) *</label>
              <input v-model="form.slug" type="text" required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="hotel-paradise-beach" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Alojamiento *</label>
              <UiSelect v-model="form.property_type" :options="propertyTypeOptions" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
              <UiSelect v-model="form.category" :options="categoryOptions" placeholder="Seleccionar..." />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción Corta</label>
              <input v-model="form.short_description" type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="Breve descripción para resultados de búsqueda (máx 150 caracteres)" maxlength="150" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción Completa</label>
              <textarea v-model="form.description" rows="6"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="Describe tu propiedad en detalle..."></textarea>
            </div>
          </div>
        </div>

        <!-- Ubicación -->
        <div v-show="activeTab === 1" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">País</label>
              <input v-model="form.country" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Provincia</label>
              <UiSelect v-model="form.province" :options="provinceOptions" placeholder="Seleccionar..." />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Región</label>
              <input v-model="form.region" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="e.g. Nicoya, Tamarindo" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ciudad</label>
              <input v-model="form.city" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Distrito</label>
              <input v-model="form.district" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Dirección Exacta</label>
              <textarea v-model="form.address" rows="2" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="Dirección completa para mostrar en el mapa"></textarea>
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">Ubicación en el Mapa</label>
              <div class="border border-gray-300 rounded-lg overflow-hidden h-80 bg-gray-100 relative">
                <div v-if="!form.latitude || !form.longitude" class="absolute inset-0 flex items-center justify-center">
                  <div class="text-center">
                    <span class="text-4xl mb-2 block">📍</span>
                    <p class="text-gray-500">Haz clic en el mapa para establecer la ubicación</p>
                    <button @click="getCurrentLocation" type="button" class="mt-2 text-primary hover:underline text-sm">
                      Usar mi ubicación actual
                    </button>
                  </div>
                </div>
                <div v-else class="absolute inset-0 flex items-center justify-center bg-blue-50">
                  <div class="text-center">
                    <span class="text-4xl mb-2 block">📍</span>
                    <p class="font-medium">Lat: {{ form.latitude.toFixed(6) }}</p>
                    <p class="font-medium">Lng: {{ form.longitude.toFixed(6) }}</p>
                    <button @click="form.latitude = null; form.longitude = null" type="button" class="mt-2 text-red-600 hover:underline text-sm">
                      Eliminar ubicación
                    </button>
                  </div>
                </div>
                <div @click="setLocationFromClick" class="absolute inset-0 cursor-crosshair"></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">Haz clic en el mapa para capturar las coordenadas</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Latitud</label>
              <input v-model.number="form.latitude" type="number" step="any" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Longitud</label>
              <input v-model.number="form.longitude" type="number" step="any" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
          </div>
        </div>

        <!-- Habitaciones -->
        <div v-show="activeTab === 2" class="space-y-6">
          <div class="flex justify-between items-center">
            <h3 class="font-medium">Habitaciones ({{ form.rooms.length }})</h3>
            <button @click="addRoom" type="button" class="text-primary hover:underline text-sm">+ Agregar habitación</button>
          </div>
          <div v-if="form.rooms.length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
            <span class="text-4xl block mb-2">🛏️</span>
            <p class="text-gray-500">No hay habitaciones agregadas</p>
            <button @click="addRoom" type="button" class="mt-2 text-primary hover:underline">Agregar primera habitación</button>
          </div>
          <div v-else class="space-y-4">
            <div v-for="(room, roomIndex) in form.rooms" :key="roomIndex" class="border border-gray-200 rounded-lg p-4">
              <div class="flex justify-between items-start mb-4">
                <h4 class="font-medium">Habitación {{ roomIndex + 1 }}</h4>
                <button @click="removeRoom(roomIndex)" type="button" class="text-red-600 hover:text-red-700 text-sm">Eliminar</button>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Nombre *</label>
                  <input v-model="room.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="Habitación Estándar" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Tipo</label>
                  <UiSelect v-model="room.room_type" :options="roomTypeOptions" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Precio por noche ($)</label>
                  <input v-model.number="room.price_per_night" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Ocupación máx.</label>
                  <input v-model.number="room.max_occupancy" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Camas</label>
                  <input v-model.number="room.bed_count" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Baños</label>
                  <input v-model.number="room.bath_count" type="number" step="0.5" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
                </div>
                <div class="md:col-span-3">
                  <label class="block text-xs font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea v-model="room.description" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" placeholder="Descripción de la habitación..."></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Amenidades -->
        <div v-show="activeTab === 3" class="space-y-6">
          <p class="text-sm text-gray-600">Selecciona las amenidades disponibles en tu propiedad:</p>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            <label v-for="amenity in availableAmenities" :key="amenity.id" class="flex items-center gap-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50" :class="form.amenities.includes(amenity.id) ? 'border-primary bg-primary/5' : ''">
              <input type="checkbox" :value="amenity.id" v-model="form.amenities" class="w-4 h-4 text-primary rounded" />
              <span>{{ amenity.icon }} {{ amenity.name }}</span>
            </label>
          </div>
        </div>

        <!-- Fotos / Videos -->
        <div v-show="activeTab === 4" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Imagen de Portada</label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <div v-if="form.cover_image" class="relative inline-block">
                <NuxtImg :src="form.cover_image" class="max-h-40 rounded-lg" width="400" format="webp" />
                <button @click="form.cover_image = ''" type="button" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">×</button>
              </div>
              <div v-else>
                <p class="text-gray-400 mb-2">Ingresa la URL de la imagen de portada</p>
                <input v-model="form.cover_image" type="url" placeholder="https://..." class="w-full max-w-md px-4 py-2 border rounded-lg text-sm" />
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Galería de Fotos</label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6">
              <div v-if="form.images.length > 0" class="grid grid-cols-3 md:grid-cols-5 gap-2 mb-4">
                <div v-for="(img, imgIdx) in form.images" :key="imgIdx" class="relative">
                  <NuxtImg :src="img" class="w-full h-20 object-cover rounded" width="150" format="webp" />
                  <button @click="removeImage(imgIdx)" type="button" class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">×</button>
                </div>
              </div>
              <div class="flex gap-2">
                <input v-model="newImageUrl" type="url" placeholder="https://..." class="flex-1 px-4 py-2 border rounded-lg text-sm" />
                <button @click="addImage" type="button" class="px-4 py-2 bg-gray-100 rounded-lg text-sm hover:bg-gray-200">Agregar</button>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Videos / Tours Virtuales</label>
            <div class="space-y-2">
              <div v-for="(video, idx) in form.videos" :key="idx" class="flex gap-2">
                <input v-model="form.videos[idx]" type="url" placeholder="URL de YouTube o Vimeo" class="flex-1 px-3 py-2 border rounded text-sm" />
                <button @click="removeVideo(idx)" type="button" class="text-red-600">×</button>
              </div>
              <button @click="addVideo" type="button" class="text-primary hover:underline text-sm">+ Agregar video</button>
            </div>
          </div>
        </div>

        <!-- Tarifas -->
        <div v-show="activeTab === 5" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Precio Base ($)</label>
              <input v-model.number="form.base_price" type="number" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Precio Fines de Semana ($)</label>
              <input v-model.number="form.weekend_price" type="number" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descuento Semanal (%)</label>
              <input v-model.number="form.weekly_discount" type="number" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="10" />
            </div>
          </div>
          <div class="flex items-center gap-2 mt-2">
            <label class="flex items-center gap-2">
              <input v-model="form.is_active" type="checkbox" class="w-4 h-4 text-primary rounded" />
              <span class="text-sm font-medium text-gray-700">Propiedad activa</span>
            </label>
          </div>
          <div class="mt-6">
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-medium">Tarifas por Temporada</h3>
              <button @click="addPricingRule" type="button" class="text-primary hover:underline text-sm">+ Agregar temporada</button>
            </div>
            <div v-if="!form.pricing_rules?.length" class="text-center py-6 bg-gray-50 rounded-lg">
              <p class="text-gray-500">No hay tarifas especiales configuradas</p>
            </div>
            <div v-else class="space-y-3">
              <div v-for="(rule, idx) in form.pricing_rules" :key="idx" class="flex gap-3 items-end p-3 bg-gray-50 rounded-lg">
                <div class="flex-1">
                  <label class="text-xs text-gray-500">Nombre</label>
                  <input v-model="rule.name" type="text" placeholder="Temporada Alta" class="w-full px-3 py-2 border rounded text-sm" />
                </div>
                <div class="flex-1">
                  <label class="text-xs text-gray-500">Desde</label>
                  <input v-model="rule.date_from" type="date" class="w-full px-3 py-2 border rounded text-sm" />
                </div>
                <div class="flex-1">
                  <label class="text-xs text-gray-500">Hasta</label>
                  <input v-model="rule.date_to" type="date" class="w-full px-3 py-2 border rounded text-sm" />
                </div>
                <div class="w-24">
                  <label class="text-xs text-gray-500">Precio ($)</label>
                  <input v-model.number="rule.price" type="number" class="w-full px-3 py-2 border rounded text-sm" />
                </div>
                <button @click="removePricingRule(idx)" type="button" class="text-red-600 pb-2">×</button>
              </div>
            </div>
          </div>
        </div>

        <!-- SEO -->
        <div v-show="activeTab === 7" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Título SEO</label>
              <input v-model="form.seo_title" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="Hotel en Tamarindo - Mejor precio garantizado" />
              <p class="text-xs text-gray-500 mt-1">{{ (form.seo_title?.length || 0) }}/60 caracteres</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">URL Amigable</label>
              <input v-model="form.seo_slug" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="hotel-tamarindo-playa" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descripción SEO</label>
              <textarea v-model="form.seo_description" rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="Descripción para motores de búsqueda..."></textarea>
              <p class="text-xs text-gray-500 mt-1">{{ (form.seo_description?.length || 0) }}/160 caracteres</p>
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Palabras Clave</label>
              <input v-model="seoKeywordsInput" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" placeholder="hotel, tamarindo, costa rica (separadas por comas)" />
            </div>
          </div>
        </div>

        <!-- Calendar - Gestión de Disponibilidad -->
        <div v-show="activeTab === 6" class="space-y-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h3 class="font-medium text-gray-900">Calendario de Disponibilidad</h3>
              <p class="text-sm text-gray-500">Gestiona la disponibilidad y precios especiales por fecha para cada habitación</p>
            </div>
          </div>

          <!-- No rooms warning -->
          <div v-if="form.rooms.length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
            <span class="text-4xl block mb-2">📅</span>
            <p class="text-gray-500">Agrega habitaciones primero en la pestaña "Habitaciones"</p>
          </div>

          <template v-else>
            <!-- Room selector -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">Habitación</label>
              <select
                v-model="calendarRoomIndex"
                class="w-full md:w-64 p-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-primary"
              >
                <option
                  v-for="(room, idx) in form.rooms"
                  :key="idx"
                  :value="idx"
                >
                  {{ room.name || `Habitación ${idx + 1}` }}
                </option>
              </select>
            </div>

            <div v-if="calendarRoomIndex !== null && form.rooms[calendarRoomIndex]" class="grid lg:grid-cols-3 gap-6">
              <!-- Calendar -->
              <div class="lg:col-span-2">
                <div class="bg-white rounded-xl border border-gray-200 p-4">
                  <div class="flex items-center justify-between mb-4">
                    <button @click="calendarPrevMonth" title="Mes anterior" class="p-1.5 hover:bg-gray-100 rounded-lg">
                      <ChevronLeft class="w-5 h-5 text-gray-600" />
                    </button>
                    <h4 class="font-semibold text-gray-900">
                      {{ calendarMonthName }} {{ calendarYear }}
                    </h4>
                    <button @click="calendarNextMonth" title="Mes siguiente" class="p-1.5 hover:bg-gray-100 rounded-lg">
                      <ChevronRight class="w-5 h-5 text-gray-600" />
                    </button>
                  </div>

                  <div class="grid grid-cols-7 mb-1">
                    <div v-for="dn in calendarDayNames" :key="dn" class="text-center text-xs font-medium text-gray-500 py-1">{{ dn }}</div>
                  </div>

                  <div class="grid grid-cols-7">
                    <div
                      v-for="(cell, idx) in calendarGrid"
                      :key="idx"
                      class="relative"
                    >
                      <button
                        v-if="!cell.isPadding"
                        @click="toggleCalendarDate(cell.date)"
                        :class="[
                          'w-full aspect-square flex flex-col items-center justify-center text-sm rounded-lg transition-colors relative',
                          getCalendarDateClass(cell.date),
                          cell.isPast ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer hover:ring-2 hover:ring-primary-300',
                        ]"
                        :disabled="cell.isPast"
                      >
                        <span>{{ cell.day }}</span>
                        <span
                          v-if="calendarPriceOverrides[cell.date] !== undefined"
                          class="text-[9px] text-amber-600 font-medium leading-none"
                        >${{ calendarPriceOverrides[cell.date] }}</span>
                        <span
                          v-if="calendarBlocked[cell.date]"
                          class="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-red-500 rounded-full"
                        ></span>
                      </button>
                      <div v-else class="w-full aspect-square"></div>
                    </div>
                  </div>

                  <!-- Legend -->
                  <div class="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                    <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-green-100 border border-green-300"></span> Disponible</span>
                    <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-red-100 border border-red-200"></span> Bloqueado</span>
                    <span class="flex items-center gap-1"><span class="w-3 h-3 rounded border-2 border-amber-400"></span> Precio especial</span>
                  </div>
                </div>
              </div>

              <!-- Controls -->
              <div class="space-y-4">
                <div class="bg-white rounded-xl border border-gray-200 p-4">
                  <h4 class="font-medium text-gray-900 mb-4">Acciones rápidas</h4>

                  <div class="space-y-3">
                    <button
                      @click="blockSelectedDates"
                      class="w-full py-2 px-4 bg-red-50 text-red-700 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors"
                    >
                      Bloquear fechas seleccionadas
                    </button>
                    <button
                      @click="unblockSelectedDates"
                      class="w-full py-2 px-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium hover:bg-green-100 transition-colors"
                    >
                      Desbloquear fechas seleccionadas
                    </button>

                    <hr class="border-gray-100" />

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Precio especial por noche</label>
                      <div class="flex gap-2">
                        <input
                          v-model.number="calendarPriceInput"
                          type="number"
                          class="flex-1 p-2 border border-gray-300 rounded-lg text-sm"
                          placeholder="$$$"
                        />
                        <button
                          @click="setPriceForSelected"
                          class="px-3 py-2 bg-primary-50 text-primary-700 rounded-lg text-sm font-medium hover:bg-primary-100"
                        >
                          Aplicar
                        </button>
                      </div>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Estadía mínima (noches)</label>
                      <div class="flex gap-2">
                        <input
                          v-model.number="calendarMinStayInput"
                          type="number"
                          min="1"
                          class="flex-1 p-2 border border-gray-300 rounded-lg text-sm"
                          placeholder="1"
                        />
                        <button
                          @click="setMinStayForSelected"
                          class="px-3 py-2 bg-primary-50 text-primary-700 rounded-lg text-sm font-medium hover:bg-primary-100"
                        >
                          Aplicar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="bg-blue-50 rounded-xl p-4 text-sm text-blue-800">
                  <p class="font-medium mb-1">💡 Tips</p>
                  <ul class="space-y-1 text-blue-700">
                    <li>• Haz clic en una fecha para bloquearla/desbloquearla</li>
                    <li>• Las fechas pasadas no se pueden modificar</li>
                    <li>• Los precios especiales sobreescriben el precio base de la habitación</li>
                  </ul>
                </div>

                <button
                  @click="saveCalendar"
                  :disabled="savingCalendar"
                  class="w-full py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <Loader2 v-if="savingCalendar" class="w-4 h-4 animate-spin" />
                  {{ savingCalendar ? 'Guardando...' : 'Guardar Calendario' }}
                </button>

                <div v-if="calendarSaveMessage" class="text-sm text-green-600 text-center">{{ calendarSaveMessage }}</div>
                <div v-if="calendarSaveError" class="text-sm text-red-600 text-center">{{ calendarSaveError }}</div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-4">{{ error }}</div>
    <div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700 mb-4">Propiedad guardada exitosamente</div>

    <!-- Actions -->
    <div class="flex justify-end gap-4">
      <NuxtLink :to="cancelUrl" class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancelar</NuxtLink>
      <button @click="saveProperty" :disabled="saving" class="bg-primary text-white px-8 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50">
        {{ saving ? 'Guardando...' : (propertyId ? 'Guardar Cambios' : 'Guardar Propiedad') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loader2, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  propertyId?: string
  cancelUrl?: string
}>(), {
  cancelUrl: '/vendor/properties'
})

const emit = defineEmits<{
  saved: []
}>()

const router = useRouter()
const api = useApi()

const propertyTypeOptions = [
  { value: 'hotel', label: 'Hotel' }, { value: 'hostel', label: 'Hostel' },
  { value: 'eco_lodge', label: 'Eco Lodge' }, { value: 'resort', label: 'Resort' },
  { value: 'villa', label: 'Villa' }, { value: 'apartment', label: 'Apartamento' },
  { value: 'cabin', label: 'Cabaña' }, { value: 'glamping', label: 'Glamping' },
  { value: 'boutique', label: 'Boutique Hotel' }, { value: 'aparthotel', label: 'Apartotel' },
]

const categoryOptions = [
  { value: 'beach', label: 'Playa' }, { value: 'mountain', label: 'Montaña' },
  { value: 'jungle', label: 'Selva' }, { value: 'city', label: 'Ciudad' },
  { value: 'rural', label: 'Rural' }, { value: 'lake', label: 'Lago' },
]

const provinceOptions = [
  { value: 'Guanacaste', label: 'Guanacaste' }, { value: 'Puntarenas', label: 'Puntarenas' },
  { value: 'Alajuela', label: 'Alajuela' }, { value: 'Cartago', label: 'Cartago' },
  { value: 'Heredia', label: 'Heredia' }, { value: 'San Jose', label: 'San José' },
  { value: 'Limon', label: 'Limón' },
]

const roomTypeOptions = [
  { value: 'standard', label: 'Estándar' }, { value: 'deluxe', label: 'Deluxe' },
  { value: 'suite', label: 'Suite' }, { value: 'family', label: 'Familiar' },
]

const availableAmenities = [
  { id: 'wifi', name: 'WiFi', icon: '📶' }, { id: 'pool', name: 'Piscina', icon: '🏊' },
  { id: 'parking', name: 'Estacionamiento', icon: '🅿️' }, { id: 'ac', name: 'A/C', icon: '❄️' },
  { id: 'restaurant', name: 'Restaurante', icon: '🍽️' }, { id: 'bar', name: 'Bar', icon: '🍸' },
  { id: 'spa', name: 'Spa', icon: '💆' }, { id: 'gym', name: 'Gimnasio', icon: '🏋️' },
  { id: 'beach', name: 'Acceso Playa', icon: '🏖️' }, { id: 'pets', name: 'Mascotas', icon: '🐕' },
  { id: 'breakfast', name: 'Desayuno', icon: '🍳' }, { id: 'room_service', name: 'Room Service', icon: '🛎️' },
  { id: 'laundry', name: 'Lavandería', icon: '👕' }, { id: 'concierge', name: 'Conserjería', icon: '🎩' },
  { id: 'security', name: 'Seguridad', icon: '🔒' }, { id: 'accessibility', name: 'Accesible', icon: '♿' },
]

const tabs = [
  { id: 'basic', label: 'Información', icon: '🏨' }, { id: 'location', label: 'Ubicación', icon: '📍' },
  { id: 'rooms', label: 'Habitaciones', icon: '🛏️' }, { id: 'amenities', label: 'Amenidades', icon: '✨' },
  { id: 'media', label: 'Fotos/Videos', icon: '📷' }, { id: 'pricing', label: 'Tarifas', icon: '💰' },
  { id: 'calendar', label: 'Calendario', icon: '📅' }, { id: 'seo', label: 'SEO', icon: '🔍' },
]

const activeTab = ref(0)
const saving = ref(false)
const error = ref('')
const success = ref(false)
const seoKeywordsInput = ref('')
const newImageUrl = ref('')

const form = reactive({
  name: '', slug: '', short_description: '', description: '',
  property_type: 'hotel', category: '',
  country: 'Costa Rica', province: '', region: '', city: '', district: '', address: '',
  latitude: null as number | null, longitude: null as number | null,
  cover_image: '', images: [] as string[], videos: [] as string[],
  amenities: [] as string[],
  check_in_time: '15:00', check_out_time: '11:00',
  min_guests: 1, max_guests: 10,
  base_price: 0, weekend_price: 0, weekly_discount: 0,
  is_active: true,
  seo_title: '', seo_description: '', seo_slug: '', seo_keywords: [] as string[],
  rooms: [] as any[], pricing_rules: [] as any[],
})

watch(() => form.name, (newName) => {
  if (!form.slug || form.slug === slugify(form.name)) {
    form.slug = slugify(newName)
  }
})

const slugify = (text: string) => {
  return text.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

const addRoom = () => {
  form.rooms.push({
    name: '', room_type: 'standard', description: '',
    max_occupancy: 2, bed_count: 1, bath_count: 1,
    price_per_night: form.base_price, amenities: []
  })
}

const removeRoom = (index: number) => { form.rooms.splice(index, 1) }
const addVideo = () => { form.videos.push('') }
const removeVideo = (index: number) => { form.videos.splice(index, 1) }
const addImage = () => {
  if (newImageUrl.value) {
    form.images.push(newImageUrl.value)
    newImageUrl.value = ''
  }
}
const removeImage = (index: number) => { form.images.splice(index, 1) }

const addPricingRule = () => {
  form.pricing_rules.push({ name: '', date_from: '', date_to: '', price: form.base_price, day_type: 'weekend' })
}
const removePricingRule = (index: number) => { form.pricing_rules.splice(index, 1) }

const setLocationFromClick = (event: MouseEvent) => {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  form.latitude = 9.7 + (1 - y / rect.height) * 1.5
  form.longitude = -85.5 + (x / rect.width) * 1.5
}

let _mounted = true
onUnmounted(() => { _mounted = false })

const getCurrentLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (!_mounted) return
        form.latitude = position.coords.latitude
        form.longitude = position.coords.longitude
      },
      (err) => {
        console.warn('Geolocation error:', err.message)
      }
    )
  }
}

const loadProperty = async () => {
  if (!props.propertyId) return
  try {
    const data = await api.get(`/properties/${props.propertyId}`)
    Object.assign(form, data)
    form.latitude = data.latitude
    form.longitude = data.longitude
    seoKeywordsInput.value = (data.seo_keywords || []).join(', ')
    newImageUrl.value = ''
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar propiedad'
  }
}

const saveProperty = async () => {
  saving.value = true
  error.value = ''
  success.value = false
  try {
    const payload = {
      ...form,
      seo_keywords: seoKeywordsInput.value.split(',').map((k: string) => k.trim()).filter(Boolean)
    }
    if (props.propertyId) {
      await api.put(`/properties/${props.propertyId}`, payload)
    } else {
      await api.post('/properties', payload)
    }
    success.value = true
    emit('saved')
    setTimeout(() => router.push(props.cancelUrl), 1500)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar propiedad'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (props.propertyId) {
    loadProperty()
  }
})

// === Calendar Management ===
const calendarRoomIndex = ref<number>(0)
const calendarCursor = ref(new Date())
const calendarBlocked = ref<Record<string, boolean>>({})
const calendarPriceOverrides = ref<Record<string, number>>({})
const calendarMinStay = ref<Record<string, number>>({})
const calendarSelected = ref<Set<string>>(new Set())
const calendarPriceInput = ref<number | null>(null)
const calendarMinStayInput = ref<number>(1)
const savingCalendar = ref(false)
const calendarSaveMessage = ref('')
const calendarSaveError = ref('')

const calendarMonthName = computed(() =>
  calendarCursor.value.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
)
const calendarYear = computed(() => calendarCursor.value.getFullYear())

const calendarDayNames = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa']

const calendarGrid = computed(() => {
  const year = calendarCursor.value.getFullYear()
  const month = calendarCursor.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const startPad = firstDay.getDay()
  const cells: { isPadding: boolean; date: string; day: number }[] = []
  for (let i = 0; i < startPad; i++) cells.push({ isPadding: true, date: '', day: 0 })
  for (let d = 1; d <= daysInMonth; d++) {
    const date = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({ isPadding: false, date, day: d })
  }
  return cells
})

const calendarPrevMonth = () => {
  calendarCursor.value = new Date(calendarCursor.value.getFullYear(), calendarCursor.value.getMonth() - 1, 1)
  calendarSelected.value.clear()
}
const calendarNextMonth = () => {
  calendarCursor.value = new Date(calendarCursor.value.getFullYear(), calendarCursor.value.getMonth() + 1, 1)
  calendarSelected.value.clear()
}

const today = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const isPastDate = (date: string) => date < today()

const toggleCalendarDate = (date: string) => {
  if (isPastDate(date)) return
  if (calendarSelected.value.has(date)) calendarSelected.value.delete(date)
  else calendarSelected.value.add(date)
}

const getCalendarDateClass = (date: string) => {
  if (isPastDate(date)) return 'text-gray-300'
  const classes: string[] = []
  if (calendarSelected.value.has(date)) classes.push('ring-2 ring-primary-500 bg-primary-50')
  else if (calendarBlocked.value[date]) classes.push('bg-red-50 text-red-800')
  else classes.push('bg-green-50 text-green-800')
  if (calendarPriceOverrides.value[date] !== undefined) classes.push('border-2 border-amber-400')
  return classes.join(' ')
}

const blockSelectedDates = () => {
  for (const date of calendarSelected.value) calendarBlocked.value[date] = true
  calendarSelected.value.clear()
}

const unblockSelectedDates = () => {
  for (const date of calendarSelected.value) delete calendarBlocked.value[date]
  calendarSelected.value.clear()
}

const setPriceForSelected = () => {
  if (!calendarPriceInput.value) return
  for (const date of calendarSelected.value) calendarPriceOverrides.value[date] = calendarPriceInput.value
  calendarSelected.value.clear()
}

const setMinStayForSelected = () => {
  if (!calendarMinStayInput.value || calendarMinStayInput.value < 1) return
  for (const date of calendarSelected.value) calendarMinStay.value[date] = calendarMinStayInput.value
  calendarSelected.value.clear()
}

const loadCalendarData = async () => {
  if (!props.propertyId || calendarRoomIndex.value === null) return
  const room = form.rooms[calendarRoomIndex.value]
  if (!room?.id) return
  try {
    const data = await api.get(`/availability/rooms/${room.id}/calendar?year=${calendarCursor.value.getFullYear()}&month=${calendarCursor.value.getMonth() + 1}`)
    calendarBlocked.value = {}
    calendarPriceOverrides.value = {}
    calendarMinStay.value = {}
    for (const day of data.days || []) {
      if (day.is_blocked) calendarBlocked.value[day.date] = true
      if (day.price_override != null) calendarPriceOverrides.value[day.date] = day.price_override
      if (day.min_stay != null) calendarMinStay.value[day.date] = day.min_stay
    }
  } catch {
    // Room may not have availability records yet
  }
}

watch(calendarRoomIndex, () => { loadCalendarData() })
watch(calendarCursor, () => { loadCalendarData() })

const buildCalendarPayload = () => {
  const entries: any[] = []
  for (const date of Object.keys(calendarBlocked.value)) entries.push({ date, is_blocked: true, price_override: calendarPriceOverrides.value[date] || null, min_stay: calendarMinStay.value[date] || null })
  for (const date of Object.keys(calendarPriceOverrides.value)) {
    if (!calendarBlocked.value[date]) entries.push({ date, is_blocked: false, price_override: calendarPriceOverrides.value[date], min_stay: calendarMinStay.value[date] || null })
  }
  for (const date of Object.keys(calendarMinStay.value)) {
    if (!calendarBlocked.value[date] && !calendarPriceOverrides.value[date]) entries.push({ date, is_blocked: false, price_override: null, min_stay: calendarMinStay.value[date] })
  }
  return entries
}

const saveCalendar = async () => {
  if (!props.propertyId || calendarRoomIndex.value === null) return
  const room = form.rooms[calendarRoomIndex.value]
  if (!room?.id) return
  savingCalendar.value = true
  calendarSaveMessage.value = ''
  calendarSaveError.value = ''
  try {
    const payload = buildCalendarPayload()
    await api.put(`/availability/rooms/${room.id}/calendar`, { entries: payload })
    calendarSaveMessage.value = 'Calendario guardado exitosamente'
    setTimeout(() => { calendarSaveMessage.value = '' }, 3000)
  } catch (e: any) {
    calendarSaveError.value = e?.data?.detail || 'Error al guardar calendario'
  } finally {
    savingCalendar.value = false
  }
}
</script>
