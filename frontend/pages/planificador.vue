<template>
  <div class="min-h-screen bg-gradient-to-br from-primary/5 via-white to-accent/5">
    <!-- Educational Hero -->
    <section class="relative bg-gradient-to-br from-primary-900 via-primary-800 to-emerald-900 py-16 px-4 overflow-hidden">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-10 left-10 w-64 h-64 bg-primary-400 rounded-full blur-3xl"></div>
        <div class="absolute bottom-10 right-10 w-80 h-80 bg-emerald-400 rounded-full blur-3xl"></div>
      </div>
      <div class="relative max-w-4xl mx-auto text-center">
        <span class="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 backdrop-blur-sm text-white text-sm rounded-full mb-4 border border-white/20">
          🗺️ Planificador Inteligente
        </span>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">{{ $t('planner.title') }}</h1>
        <p class="text-lg text-white/80 max-w-2xl mx-auto">{{ $t('planner.subtitle') }}</p>
        <div class="mt-6 flex flex-wrap justify-center gap-3 text-sm text-white/60">
          <span class="flex items-center gap-1">✓ Datos verificados</span>
          <span class="flex items-center gap-1">✓ Presupuesto transparente</span>
          <span class="flex items-center gap-1">✓ Rutas optimizadas</span>
          <span class="flex items-center gap-1">✓ Recomendaciones locales</span>
        </div>
      </div>
    </section>

    <div class="max-w-5xl mx-auto px-4 -mt-6 relative z-10">
      <!-- Progress Bar -->
      <div class="bg-white rounded-2xl shadow-lg p-4 md:p-6 mb-6 border border-gray-100">
        <div class="flex justify-between items-center">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center"
            :class="{ 'flex-1': index < steps.length - 1 }"
          >
            <div class="flex flex-col items-center">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-300"
                :class="currentStep > index + 1 ? 'bg-green-500 text-white shadow-lg shadow-green-200' : currentStep === index + 1 ? 'bg-primary text-white shadow-lg shadow-primary-200' : 'bg-gray-100 text-gray-400'"
              >
                <span v-if="currentStep > index + 1">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                  </svg>
                </span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span class="text-xs mt-1 hidden sm:block"
                :class="currentStep === index + 1 ? 'text-primary font-semibold' : currentStep > index + 1 ? 'text-green-600' : 'text-gray-400'"
              >{{ step }}</span>
            </div>
            <div v-if="index < steps.length - 1" class="flex-1 h-0.5 mx-2 md:mx-4 bg-gray-100 rounded">
              <div
                class="h-full bg-gradient-to-r from-primary to-green-500 rounded transition-all duration-500"
                :style="{ width: currentStep > index + 1 ? '100%' : '0%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="bg-white rounded-2xl shadow-lg p-6 md:p-8 border border-gray-100 mb-8">

        <!-- STEP 1: Duration + Budget -->
        <div v-show="currentStep === 1" class="space-y-6">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-3xl">📅</span>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ $t('step1.title') }}</h2>
              <p class="text-gray-500">Elige cuántos días y tu presupuesto estimado</p>
            </div>
          </div>

          <div class="grid md:grid-cols-3 gap-4">
            <div
              v-for="option in durationOptions"
              :key="option.value"
              @click="form.duration = option.value"
              class="relative p-5 border-2 rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md"
              :class="form.duration === option.value ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-gray-200 hover:border-primary/40'"
            >
              <div v-if="form.duration === option.value" class="absolute top-3 right-3 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <div class="text-4xl mb-3">{{ option.icon }}</div>
              <h3 class="font-bold text-gray-900 text-lg">{{ option.label }}</h3>
              <p class="text-sm text-gray-500 mt-1">{{ option.desc }}</p>
              <div class="mt-3 pt-3 border-t border-gray-100">
                <p class="text-xs text-gray-400">
                  <span class="font-medium text-gray-600">Perfecto para:</span> {{ option.perfectFor }}
                </p>
              </div>
            </div>
          </div>

          <!-- Budget Slider con breakdown educativo -->
          <div class="p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-200">
            <div class="flex items-center justify-between mb-6">
              <div>
                <label class="block font-bold text-gray-900 text-lg">💰 Presupuesto estimado</label>
                <p class="text-sm text-gray-500">Por persona • Incluye alojamiento, comidas, actividades y transporte local</p>
              </div>
              <div class="text-right">
                <span class="text-3xl font-bold text-primary">${{ form.budget.toLocaleString() }}</span>
                <p class="text-xs text-gray-400">por persona</p>
              </div>
            </div>
            <input
              type="range"
              v-model.number="form.budget"
              min="500"
              max="10000"
              step="100"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div class="flex justify-between mt-2 text-xs text-gray-400">
              <span>$500</span>
              <span>$2,500</span>
              <span>$5,000</span>
              <span>$7,500</span>
              <span>$10,000</span>
            </div>

            <!-- Budget allocation estimate -->
            <div v-if="form.duration" class="mt-6 grid grid-cols-4 gap-3">
              <div class="bg-white rounded-lg p-3 text-center border border-gray-100">
                <div class="text-xs text-gray-500">🏨 Alojamiento</div>
                <div class="font-bold text-gray-800 text-sm mt-1">~{{ housingPct }}%</div>
              </div>
              <div class="bg-white rounded-lg p-3 text-center border border-gray-100">
                <div class="text-xs text-gray-500">🍽️ Comidas</div>
                <div class="font-bold text-gray-800 text-sm mt-1">~{{ foodPct }}%</div>
              </div>
              <div class="bg-white rounded-lg p-3 text-center border border-gray-100">
                <div class="text-xs text-gray-500">🎯 Actividades</div>
                <div class="font-bold text-gray-800 text-sm mt-1">~{{ activitiesPct }}%</div>
              </div>
              <div class="bg-white rounded-lg p-3 text-center border border-gray-100">
                <div class="text-xs text-gray-500">🚗 Transporte</div>
                <div class="font-bold text-gray-800 text-sm mt-1">~{{ transportPct }}%</div>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 2: Travel Style -->
        <div v-show="currentStep === 2" class="space-y-6">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-3xl">🎯</span>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ $t('step2.title') }}</h2>
              <p class="text-gray-500">Selecciona cómo quieres vivir tu viaje</p>
            </div>
          </div>

          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="option in styleOptions"
              :key="option.value"
              @click="form.style = option.value"
              class="relative p-5 border-2 rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md"
              :class="form.style === option.value ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-gray-200 hover:border-primary/40'"
            >
              <div v-if="form.style === option.value" class="absolute top-3 right-3 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <div class="text-4xl mb-3">{{ option.icon }}</div>
              <h3 class="font-bold text-gray-900 text-lg">{{ option.label }}</h3>
              <p class="text-sm text-gray-500 mt-1">{{ option.desc }}</p>
              <div class="mt-3 pt-3 border-t border-gray-100">
                <span class="inline-flex items-center gap-1 text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded">
                  {{ option.activityCount }} actividades
                </span>
                <span class="inline-flex items-center gap-1 text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded ml-2">
                  {{ option.difficulty }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 3: Destinations -->
        <div v-show="currentStep === 3" class="space-y-6">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-3xl">📍</span>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ $t('step3.title') }}</h2>
              <p class="text-gray-500">Selecciona uno o más destinos para tu itinerario</p>
            </div>
          </div>

          <!-- Selected count badge -->
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <span class="font-semibold text-primary">{{ form.destinations.length }}</span> destino(s) seleccionado(s)
            <span v-if="form.destinations.length >= 2" class="text-green-600 flex items-center gap-1 ml-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
              Ruta multi-destino posible
            </span>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div
              v-for="dest in destinationOptions"
              :key="dest.value"
              @click="toggleDestination(dest.value)"
              class="relative p-5 border-2 rounded-xl cursor-pointer transition-all duration-200 hover:shadow-md"
              :class="form.destinations.includes(dest.value) ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-gray-200 hover:border-primary/40'"
            >
              <div class="flex items-start gap-4">
                <div class="text-4xl flex-shrink-0">{{ dest.icon }}</div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <h3 class="font-bold text-gray-900 text-lg">{{ dest.label }}</h3>
                    <div
                      class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all"
                      :class="form.destinations.includes(dest.value) ? 'bg-primary text-white' : 'bg-gray-200'"
                    >
                      <span v-if="form.destinations.includes(dest.value)">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                        </svg>
                      </span>
                    </div>
                  </div>
                  <p class="text-sm text-gray-500 mt-1">{{ dest.desc }}</p>

                  <!-- Quick facts -->
                  <div class="mt-3 flex flex-wrap gap-2">
                    <span class="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                      🌡️ {{ dest.temp }}°C
                    </span>
                    <span class="inline-flex items-center gap-1 text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded">
                      🏆 {{ dest.bestFor }}
                    </span>
                    <span class="inline-flex items-center gap-1 text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded">
                      🕐 {{ dest.fromSJO }}
                    </span>
                  </div>

                  <!-- Show transit info if another destination is selected -->
                  <div v-if="form.destinations.length > 0 && form.destinations[form.destinations.length-1] !== dest.value" class="mt-3 pt-3 border-t border-gray-100">
                    <p class="text-xs text-gray-400">
                      Desde {{ getLastSelectedDest() }}:
                      <span class="font-medium text-gray-600">{{ getTransitInfo(dest.value) }}</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 4: Details + Season Guide -->
        <div v-show="currentStep === 4" class="space-y-6">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-3xl">⚙️</span>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ $t('step4.title') }}</h2>
              <p class="text-gray-500">Personaliza los detalles finales de tu viaje</p>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <label class="block font-semibold text-gray-700 mb-2">{{ $t('step4.travelers') }}</label>
              <div class="grid grid-cols-5 gap-2">
                <button
                  v-for="opt in travelerOptions"
                  :key="opt.value"
                  @click="form.travelers = opt.value"
                  class="py-3 rounded-lg border-2 font-semibold transition-all"
                  :class="form.travelers === opt.value ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 text-gray-600 hover:border-gray-300'"
                >{{ opt.label }}</button>
              </div>
            </div>
            <div>
              <label class="block font-semibold text-gray-700 mb-2">{{ $t('step4.season') }}</label>
              <div class="grid grid-cols-1 gap-2">
                <button
                  v-for="opt in seasonOptions"
                  :key="opt.value"
                  @click="form.season = opt.value"
                  class="py-3 px-4 rounded-lg border-2 font-semibold text-left transition-all flex items-center gap-3"
                  :class="form.season === opt.value ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 text-gray-600 hover:border-gray-300'"
                >
                  <span>{{ opt.icon }}</span>
                  <span>{{ opt.label }}</span>
                  <span class="text-xs text-gray-400 ml-auto">{{ opt.months }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Season guide (educational) -->
          <div class="p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
            <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <span>🌤️</span> Guía de temporada para tus destinos
            </h4>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-blue-200">
                    <th class="text-left py-2 pr-4 font-semibold text-gray-700">Destino</th>
                    <th v-for="m in months" :key="m" class="py-2 px-1 text-center text-xs font-semibold text-gray-600 w-10">{{ m }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="dest in selectedDestDetails" :key="dest.value" class="border-b border-blue-100">
                    <td class="py-2 pr-4 font-medium text-gray-700">{{ dest.label }}</td>
                    <td v-for="(emoji, mIdx) in dest.monthlyWeather" :key="mIdx" class="py-2 px-1 text-center text-xs">
                      <span :title="emoji.tip">{{ emoji.icon }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-xs text-gray-500 mt-3">
              ☀️ = Seco • 🌧️ = Lluvioso • ⛅ = Variable • 🌤️ = Buen tiempo
            </p>
            <p v-if="form.season === 'dec-apr'" class="text-xs text-green-600 mt-2 font-medium">
              ✅ Temporada seca — ideal para playas y actividades al aire libre. Mayor demanda, precios más altos.
            </p>
            <p v-else-if="form.season === 'may-nov'" class="text-xs text-amber-600 mt-2 font-medium">
              🍃 Temporada verde — menos turistas, selva exuberante, mejores precios. Lluvias suelen ser por la tarde.
            </p>
            <p v-else class="text-xs text-gray-500 mt-2 font-medium">
              💡 Sin preferencia de fecha. Recomendaremos la mejor época según tus destinos.
            </p>
          </div>

          <!-- Transport preference -->
          <div>
            <label class="block font-semibold text-gray-700 mb-3">🚗 Transporte preferido</label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                v-for="opt in transportOptions"
                :key="opt.value"
                @click="form.transport = opt.value"
                class="py-3 px-4 rounded-lg border-2 font-semibold text-sm transition-all text-center"
                :class="form.transport === opt.value ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 text-gray-500 hover:border-gray-300'"
              >
                <div class="text-2xl mb-1">{{ opt.icon }}</div>
                <div>{{ opt.label }}</div>
                <div class="text-xs text-gray-400 font-normal">{{ opt.detail }}</div>
              </button>
            </div>
          </div>

          <!-- Accommodation preference -->
          <div>
            <label class="block font-semibold text-gray-700 mb-2">🏨 Tipo de alojamiento</label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                v-for="opt in accommodationOptions"
                :key="opt.value"
                @click="form.accommodation = opt.value"
                class="py-3 px-4 rounded-lg border-2 font-semibold text-sm transition-all text-center"
                :class="form.accommodation === opt.value ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 text-gray-500 hover:border-gray-300'"
              >
                <div class="text-2xl mb-1">{{ opt.icon }}</div>
                <div>{{ opt.label }}</div>
                <div class="text-xs text-gray-400 font-normal">{{ opt.priceRange }}</div>
              </button>
            </div>
          </div>

          <div>
            <label class="block font-semibold text-gray-700 mb-2">📝 {{ $t('step4.notes') }}</label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none resize-none transition-all"
              placeholder="Ej: Viajo con niños pequeños, soy vegetariano, tengo movilidad reducida, quiero celebrar un aniversario..."
            ></textarea>
          </div>

          <!-- Budget Summary -->
          <div class="p-6 bg-gradient-to-r from-primary via-primary-600 to-primary-700 rounded-xl text-white shadow-lg">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-bold text-lg">📊 Resumen de Inversión</h3>
              <span class="text-sm opacity-80">por persona</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                <p class="text-sm opacity-80">Presupuesto</p>
                <p class="text-2xl font-bold">${{ form.budget.toLocaleString() }}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                <p class="text-sm opacity-80">Viajeros</p>
                <p class="text-2xl font-bold">{{ form.travelers }} {{ form.travelers === 1 ? 'persona' : 'personas' }}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                <p class="text-sm opacity-80">Total grupo</p>
                <p class="text-2xl font-bold">${{ (form.budget * form.travelers).toLocaleString() }}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg p-3">
                <p class="text-sm opacity-80">Días</p>
                <p class="text-2xl font-bold">{{ durationDays }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 5: Result -->
        <div v-show="currentStep === 5" class="space-y-8">
          <div class="text-center">
            <div class="text-6xl mb-4 inline-block bg-gradient-to-br from-primary/10 to-accent/10 p-6 rounded-full">🎉</div>
            <h2 class="text-3xl font-bold text-gray-900">{{ $t('step5.title') }}</h2>
            <p class="text-gray-500 mt-2 max-w-xl mx-auto">
              {{ generatedItinerary.length }} días • {{ form.destinations.length }} destino(s) • Presupuesto ${{ form.budget.toLocaleString() }}/persona
            </p>
          </div>

          <!-- Trip Summary Cards -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-4 text-center">
              <div class="text-3xl mb-2">🗓️</div>
              <div class="text-2xl font-bold text-primary-600">{{ durationDays }}</div>
              <div class="text-sm text-gray-600">Días</div>
            </div>
            <div class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 text-center">
              <div class="text-3xl mb-2">📍</div>
              <div class="text-2xl font-bold text-amber-600">{{ form.destinations.length }}</div>
              <div class="text-sm text-gray-600">Destinos</div>
            </div>
            <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
              <div class="text-3xl mb-2">🎯</div>
              <div class="text-2xl font-bold text-green-600">{{ totalActivities }}</div>
              <div class="text-sm text-gray-600">Actividades</div>
            </div>
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
              <div class="text-3xl mb-2">💰</div>
              <div class="text-2xl font-bold text-purple-600">${{ estimatedTotal }}</div>
              <div class="text-sm text-gray-600">Costo estimado</div>
            </div>
          </div>

          <!-- Cost breakdown bar -->
          <div class="bg-gray-50 rounded-xl p-5">
            <h4 class="font-semibold text-gray-900 mb-3">📊 Distribución del presupuesto</h4>
            <div class="space-y-2">
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>🏨 Alojamiento</span>
                  <span class="font-medium">{{ costBreakdown.housingPct }}% (${{ costBreakdown.housing }})</span>
                </div>
                <div class="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-blue-500 rounded-full transition-all" :style="{ width: costBreakdown.housingPct + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>🍽️ Comidas</span>
                  <span class="font-medium">{{ costBreakdown.foodPct }}% (${{ costBreakdown.food }})</span>
                </div>
                <div class="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-green-500 rounded-full transition-all" :style="{ width: costBreakdown.foodPct + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>🎯 Actividades</span>
                  <span class="font-medium">{{ costBreakdown.activitiesPct }}% (${{ costBreakdown.activities }})</span>
                </div>
                <div class="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-amber-500 rounded-full transition-all" :style="{ width: costBreakdown.activitiesPct + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>🚗 Transporte</span>
                  <span class="font-medium">{{ costBreakdown.transportPct }}% (${{ costBreakdown.transport }})</span>
                </div>
                <div class="h-2.5 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-purple-500 rounded-full transition-all" :style="{ width: costBreakdown.transportPct + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Itinerary Timeline -->
          <div class="relative">
            <div class="absolute left-6 md:left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary via-primary-400 to-primary-200"></div>

            <div
              v-for="(day, index) in generatedItinerary"
              :key="index"
              class="relative pl-14 md:pl-20 pb-10 last:pb-0"
            >
              <div class="absolute left-4 md:left-6 w-5 h-5 bg-white border-4 border-primary rounded-full shadow-md z-10"></div>
              <div class="absolute left-3 md:left-5 -top-1 w-8 h-8 bg-primary/10 rounded-full blur-sm"></div>

              <div class="bg-white rounded-xl p-5 md:p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                <!-- Day header -->
                <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                  <div>
                    <span class="inline-flex items-center gap-2 text-sm text-primary-600 font-semibold mb-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                      </svg>
                      Día {{ index + 1 }}
                    </span>
                    <h3 class="text-xl font-bold text-gray-900">{{ day.title }}</h3>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="px-3 py-1.5 bg-primary/10 text-primary text-sm font-medium rounded-full">
                      {{ day.region }}
                    </span>
                    <span class="px-3 py-1.5 bg-green-50 text-green-700 text-xs font-medium rounded-full">
                      ${{ day.dayCost }}/persona
                    </span>
                  </div>
                </div>

                <!-- Activities -->
                <div class="space-y-3">
                  <div
                    v-for="(activity, aIdx) in day.activities"
                    :key="aIdx"
                    class="flex items-start gap-3"
                  >
                    <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm"
                      :class="getActivityColor(aIdx)"
                    >
                      {{ getActivityIcon(aIdx) }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between">
                        <span class="text-sm font-semibold text-gray-800">{{ activity.time }}</span>
                        <span v-if="activity.cost" class="text-xs text-gray-400">+${{ activity.cost }}</span>
                      </div>
                      <p class="text-sm text-gray-600">{{ activity.desc }}</p>
                      <p v-if="activity.detail" class="text-xs text-gray-400 mt-0.5">{{ activity.detail }}</p>
                    </div>
                  </div>
                </div>

                <!-- Day Cost Breakdown -->
                <div class="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500 flex flex-wrap gap-x-4 gap-y-1">
                  <span>🏨 Alojamiento: <span class="font-medium text-gray-700">${{ day.costs.housing }}</span></span>
                  <span>🍽️ Comidas: <span class="font-medium text-gray-700">${{ day.costs.food }}</span></span>
                  <span>🎯 Actividades: <span class="font-medium text-gray-700">${{ day.costs.activities }}</span></span>
                  <span>🚗 Transporte local: <span class="font-medium text-gray-700">${{ day.costs.transport }}</span></span>
                </div>

                <!-- Tip -->
                <div class="mt-3 p-4 bg-gradient-to-r from-accent/5 to-accent/10 rounded-xl border border-accent/20 flex items-start gap-3">
                  <span class="text-xl flex-shrink-0">💡</span>
                  <div>
                    <span class="text-xs font-semibold text-accent uppercase tracking-wide">Consejo local</span>
                    <p class="text-sm text-gray-700 mt-0.5">{{ day.tip }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Save / Export -->
          <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
            <div class="flex flex-wrap justify-center gap-3">
              <button @click="printItinerary" class="px-6 py-3 bg-white text-gray-700 rounded-xl border border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all flex items-center gap-2 shadow-sm">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
                </svg>
                {{ $t('step5.print') }}
              </button>
              <button @click="copyItinerary" class="px-6 py-3 bg-white text-gray-700 rounded-xl border border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all flex items-center gap-2 shadow-sm">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                </svg>
                Copiar
              </button>
              <button @click="shareItinerary" class="px-6 py-3 bg-white text-gray-700 rounded-xl border border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all flex items-center gap-2 shadow-sm">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
                </svg>
                Compartir
              </button>
              <button @click="resetPlanner" class="px-6 py-3 bg-primary text-white rounded-xl hover:bg-primary-700 transition-all flex items-center gap-2 shadow-lg shadow-primary-200">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                {{ $t('step5.reset') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-between mt-8 pt-6 border-t border-gray-100">
          <button
            v-if="currentStep > 1"
            @click="prevStep"
            class="px-6 py-3 bg-gray-50 text-gray-700 rounded-xl hover:bg-gray-100 transition-all flex items-center gap-2 border border-gray-200"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            {{ $t('nav.prev') }}
          </button>
          <div v-else></div>

          <button
            v-if="currentStep < 5"
            @click="nextStep"
            :disabled="saving"
            class="px-8 py-3 bg-primary text-white rounded-xl hover:bg-primary-700 active:bg-primary-800 disabled:opacity-60 disabled:cursor-wait transition-all flex items-center gap-2 shadow-lg shadow-primary-200"
          >
            <span v-if="saving" class="flex items-center gap-2">
              <UiSpinner size="sm" color="primary" />
              Guardando...
            </span>
            <span v-else-if="currentStep === 4">✨ {{ $t('planner.generate') }}</span>
            <span v-else>{{ $t('nav.next') }}</span>
            <svg v-if="!saving" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const toast = useToast()

useSeo({
  title: 'Planificador de Viaje Inteligente',
  description: 'Planifica tu viaje ideal a Costa Rica con nuestro planificador interactivo. Datos verificados, presupuesto transparente, rutas optimizadas y recomendaciones locales.',
  keywords: 'planificador viaje Costa Rica, itinerario, ruta Costa Rica, presupuesto viaje, planificar vacaciones, viaje personalizado, tour planner',
  ogType: 'website'
})

useJsonLd({
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: 'Planificador de Viaje Inteligente - Costa Rica',
  description: 'Planificador interactivo de viajes con datos verificados, presupuesto transparente y recomendaciones locales para Costa Rica',
  url: 'https://costaricatravel.dev/planificador',
  applicationCategory: 'TravelApplication',
  operatingSystem: 'All',
  browserRequirements: 'Requires JavaScript'
})

const currentStep = ref(1)
const steps = ['Duración', 'Estilo', 'Destinos', 'Detalles', 'Resultado']

const months = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

const form = reactive({
  duration: null as string | null,
  budget: 1500,
  style: null as string | null,
  destinations: [] as string[],
  travelers: 2,
  season: 'any',
  transport: 'shuttle',
  accommodation: 'mid',
  notes: ''
})

const durationOptions = [
  {
    value: '3-5', icon: '🌟', label: 'Corto pero intenso', desc: '3-5 días',
    perfectFor: 'Escapadas, conexiones, eventos especiales'
  },
  {
    value: '7-10', icon: '⭐', label: 'Viaje completo', desc: '7-10 días',
    perfectFor: '2-3 destinos, ritmo relajado, inmersión cultural'
  },
  {
    value: '14+', icon: '🏆', label: 'Aventura total', desc: '14+ días',
    perfectFor: 'Exploración profunda, múltiples regiones, viajeros experimentados'
  }
]

const styleOptions = [
  {
    value: 'relax', icon: '🏖️', label: 'Relax & Playa', desc: 'Desconexión total frente al mar',
    activityCount: 8, difficulty: 'Baja'
  },
  {
    value: 'adventure', icon: '🧗', label: 'Aventura', desc: 'Adrenalina y desafíos',
    activityCount: 15, difficulty: 'Media-Alta'
  },
  {
    value: 'nature', icon: '🌿', label: 'Naturaleza', desc: 'Fauna, flora y conservación',
    activityCount: 12, difficulty: 'Media'
  },
  {
    value: 'culture', icon: '🏛️', label: 'Cultura', desc: 'Historia, gastronomía, arte local',
    activityCount: 10, difficulty: 'Baja-Media'
  },
  {
    value: 'romance', icon: '💕', label: 'Romance', desc: 'Escapadas íntimas en pareja',
    activityCount: 9, difficulty: 'Baja'
  },
  {
    value: 'family', icon: '👨‍👩‍👧', label: 'Familia', desc: 'Actividades para todas las edades',
    activityCount: 11, difficulty: 'Baja'
  }
]

const destinationOptions = [
  {
    value: 'guanacaste', icon: '🏖️', label: 'Guanacaste', desc: 'Playas doradas, sol y surf de clase mundial',
    temp: '28-33', bestFor: 'Playas, surf, atardeceres', fromSJO: '4h en auto / 50min vuelo',
    monthlyWeather: [
      { icon: '☀️', tip: 'Temporada seca, ideal' },
      { icon: '☀️', tip: 'Temporada seca, ideal' },
      { icon: '☀️', tip: 'Temporada seca, calor intenso' },
      { icon: '☀️', tip: 'Final de temporada seca' },
      { icon: '⛅', tip: 'Inicio de lluvias, aún disfrutable' },
      { icon: '🌧️', tip: 'Temporada lluviosa' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '🌧️', tip: 'Lluvias fuertes' },
      { icon: '⛅', tip: 'Transición, menos lluvia' },
      { icon: '☀️', tip: 'Inicio temporada seca' },
      { icon: '☀️', tip: 'Temporada seca, Navidad' }
    ]
  },
  {
    value: 'arenal', icon: '🌋', label: 'Arenal', desc: 'Volcán activo, aguas termales, aventura',
    temp: '22-28', bestFor: 'Termales, senderismo, canopy', fromSJO: '3h en auto',
    monthlyWeather: [
      { icon: '☀️', tip: 'Temporada seca, cielo despejado' },
      { icon: '☀️', tip: 'Excelente visibilidad del volcán' },
      { icon: '⛅', tip: 'Variable, aún buena vista' },
      { icon: '⛅', tip: 'Transición, nubes parciales' },
      { icon: '🌧️', tip: 'Inicio lluvias, termales en la lluvia' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '🌧️', tip: 'Máximas lluvias' },
      { icon: '🌧️', tip: 'Lluvias intensas' },
      { icon: '🌧️', tip: 'Lluvias fuertes' },
      { icon: '⛅', tip: 'Mejora el clima' },
      { icon: '☀️', tip: 'Vuelve la temporada seca' },
      { icon: '☀️', tip: 'Temporada seca' }
    ]
  },
  {
    value: 'monteverde', icon: '☁️', label: 'Monteverde', desc: 'Bosque nuboso, quetzales y canopy',
    temp: '16-22', bestFor: 'Naturaleza, aves, ecoturismo', fromSJO: '3.5h en auto',
    monthlyWeather: [
      { icon: '☀️', tip: 'Menos nubes, mejor visibilidad' },
      { icon: '⛅', tip: 'Todavía buena' },
      { icon: '⛅', tip: 'Variable' },
      { icon: '🌧️', tip: 'Inicio lluvias' },
      { icon: '🌧️', tip: 'Lluvioso pero exuberante' },
      { icon: '🌧️', tip: 'Muy lluvioso' },
      { icon: '🌧️', tip: 'Muy lluvioso, senderos mojados' },
      { icon: '🌧️', tip: 'Fuertes lluvias' },
      { icon: '🌧️', tip: 'Lluvias intensas' },
      { icon: '🌧️', tip: 'Transición, menos lluvia' },
      { icon: '⛅', tip: 'Mejora significativa' },
      { icon: '☀️', tip: 'Temporada seca' }
    ]
  },
  {
    value: 'manuel', icon: '🦁', label: 'Manuel Antonio', desc: 'Playa y vida salvaje en un paraíso',
    temp: '24-30', bestFor: 'Fauna, playa, snorkel', fromSJO: '3h en auto',
    monthlyWeather: [
      { icon: '☀️', tip: 'Temporada seca, ideal playa' },
      { icon: '☀️', tip: 'Excelente' },
      { icon: '☀️', tip: 'Calor intenso' },
      { icon: '⛅', tip: 'Transición, aún bueno' },
      { icon: '🌧️', tip: 'Inicio lluvias tropicales' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '🌧️', tip: 'Lluvias intensas' },
      { icon: '🌧️', tip: 'Lluvias fuertes' },
      { icon: '🌧️', tip: 'Lluvias, menos turistas' },
      { icon: '🌧️', tip: 'Transición' },
      { icon: '⛅', tip: 'Mejora' },
      { icon: '☀️', tip: 'Temporada seca' }
    ]
  },
  {
    value: 'caribe', icon: '🌴', label: 'Caribe Sur', desc: 'Aguas turquesa, cultura afrocaribeña y reggae',
    temp: '24-30', bestFor: 'Snorkel, cultura, relax', fromSJO: '3.5h en auto',
    monthlyWeather: [
      { icon: '⛅', tip: 'Variable, buen clima' },
      { icon: '⛅', tip: 'Variable' },
      { icon: '⛅', tip: 'Puede llover' },
      { icon: '⛅', tip: 'Variable' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '🌧️', tip: 'Máximas lluvias' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '⛅', tip: 'Mejora' },
      { icon: '⛅', tip: 'Transición' },
      { icon: '⛅', tip: 'Buen tiempo' },
      { icon: '⛅', tip: 'Variable' },
      { icon: '⛅', tip: 'Navidad, clima agradable' }
    ]
  },
  {
    value: 'central', icon: '🏛️', label: 'Valle Central', desc: 'San José, cultura, museos y cafés de altura',
    temp: '18-25', bestFor: 'Historia, café, gastronomía', fromSJO: 'En la ciudad',
    monthlyWeather: [
      { icon: '☀️', tip: 'Temporada seca' },
      { icon: '☀️', tip: 'Temporada seca' },
      { icon: '☀️', tip: 'Calor moderado' },
      { icon: '☀️', tip: 'Final temporada seca' },
      { icon: '⛅', tip: 'Inicio lluvias vespertinas' },
      { icon: '🌧️', tip: 'Lluvias por la tarde' },
      { icon: '🌧️', tip: 'Lluvias frecuentes' },
      { icon: '🌧️', tip: 'Lluvias intensas' },
      { icon: '🌧️', tip: 'Lluvias fuertes' },
      { icon: '🌧️', tip: 'Transición' },
      { icon: '⛅', tip: 'Mejora' },
      { icon: '☀️', tip: 'Temporada seca' }
    ]
  }
]

const travelerOptions = [
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 4, label: '4' },
  { value: 5, label: '5+' }
]

const seasonOptions = [
  { value: 'any', icon: '📅', label: 'Sin preferencia', months: 'Cualquier fecha' },
  { value: 'dec-apr', icon: '☀️', label: 'Temporada Seca', months: 'Diciembre - Abril' },
  { value: 'may-nov', icon: '🌿', label: 'Temporada Verde', months: 'Mayo - Noviembre' }
]

const transportOptions = [
  { value: 'shuttle', icon: '🚐', label: 'Shuttle', detail: 'Cómodo y social' },
  { value: 'rental', icon: '🚗', label: 'Auto rentado', detail: 'Máxima libertad' },
  { value: 'private', icon: '🚙', label: 'Transfer privado', detail: 'Exclusivo' },
  { value: 'public', icon: '🚌', label: 'Bus público', detail: 'Económico' }
]

const accommodationOptions = [
  { value: 'budget', icon: '🏕️', label: 'Económico', priceRange: '$20-50/noche' },
  { value: 'mid', icon: '🏨', label: 'Estándar', priceRange: '$50-150/noche' },
  { value: 'premium', icon: '🏰', label: 'Premium', priceRange: '$150-350/noche' },
  { value: 'luxury', icon: '👑', label: 'Lujo', priceRange: '$350+/noche' }
]

const destinationMap = computed(() => {
  const map: Record<string, any> = {}
  for (const d of destinationOptions) map[d.value] = d
  return map
})

const selectedDestDetails = computed(() =>
  form.destinations.map(v => destinationMap.value[v]).filter(Boolean)
)

const durationDays = computed(() => {
  if (form.duration === '3-5') return 4
  if (form.duration === '7-10') return 8
  if (form.duration === '14+') return 14
  return 4
})

const housingPct = computed(() => form.budget <= 1000 ? 35 : form.budget <= 3000 ? 40 : form.budget <= 6000 ? 45 : 50)
const foodPct = computed(() => form.budget <= 1000 ? 30 : 25)
const activitiesPct = computed(() => form.budget <= 1000 ? 20 : 25)
const transportPct = computed(() => 100 - housingPct.value - foodPct.value - activitiesPct.value)

const canProceed = computed(() => {
  if (currentStep.value === 1) return form.duration !== null
  if (currentStep.value === 2) return form.style !== null
  if (currentStep.value === 3) return form.destinations.length > 0
  if (currentStep.value === 4) return true
  return true
})

const getLastSelectedDest = () => {
  if (form.destinations.length < 2) return 'San José (SJO)'
  const last = form.destinations[form.destinations.length - 2]
  const d = destinationMap.value[last]
  return d ? d.label : 'Destino anterior'
}

const transitData: Record<string, Record<string, string>> = {
  guanacaste: { arenal: '2h en auto', monteverde: '3h en auto', manuel: '4.5h en auto', caribe: '6h en auto', central: '4h en auto' },
  arenal: { guanacaste: '2h en auto', monteverde: '2.5h en auto', manuel: '4h en auto', caribe: '5h en auto', central: '3h en auto' },
  monteverde: { guanacaste: '3h en auto', arenal: '2.5h en auto', manuel: '4h en auto', caribe: '5h en auto', central: '3.5h en auto' },
  manuel: { guanacaste: '4.5h en auto', arenal: '4h en auto', monteverde: '4h en auto', caribe: '3h en auto', central: '3h en auto' },
  caribe: { guanacaste: '6h en auto', arenal: '5h en auto', monteverde: '5h en auto', manuel: '3h en auto', central: '3.5h en auto' },
  central: { guanacaste: '4h en auto', arenal: '3h en auto', monteverde: '3.5h en auto', manuel: '3h en auto', caribe: '3.5h en auto' }
}

const getTransitInfo = (dest: string): string => {
  if (form.destinations.length < 2) return ''
  const prev = form.destinations[form.destinations.length - 2]
  return transitData[prev]?.[dest] || 'Consultar ruta'
}

const toggleDestination = (value: string) => {
  const index = form.destinations.indexOf(value)
  if (index > -1) {
    form.destinations.splice(index, 1)
  } else {
    form.destinations.push(value)
  }
}

const saving = ref(false)

const nextStep = async () => {
  if (!canProceed.value) {
    const messages: Record<number, string> = {
      1: 'Seleccioná la duración de tu viaje primero',
      2: 'Elegí tu estilo de viaje favorito',
      3: 'Seleccioná al menos un destino'
    }
    toast.error(messages[currentStep.value] || 'Completá los campos requeridos')
    return
  }
  if (currentStep.value < 5) {
    if (currentStep.value === 4) {
      saving.value = true
      await generateItinerary()
      await saveLead()
      saving.value = false
    }
    currentStep.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// ---- Itinerary Generation ----
const generatedItinerary = ref<any[]>([])
const totalActivities = ref(0)
const estimatedTotal = ref(0)

const costBreakdown = computed(() => {
  const housing = Math.round(form.budget * housingPct.value / 100)
  const food = Math.round(form.budget * foodPct.value / 100)
  const activities = Math.round(form.budget * activitiesPct.value / 100)
  const transport = form.budget - housing - food - activities
  return {
    housingPct: housingPct.value,
    foodPct: foodPct.value,
    activitiesPct: activitiesPct.value,
    transportPct: transportPct.value,
    housing, food, activities, transport
  }
})

const destInfo: Record<string, any> = {
  guanacaste: { region: 'Guanacaste', icon: '🏖️', tip: 'No te pierdas el atardecer en Playa Conchal. Prueba el ceviche en los sodas locales.', altTip: 'Visita el Parque Nacional Rincón de la Vieja para senderismo y aguas termales naturales.' },
  arenal: { region: 'Arenal', icon: '🌋', tip: 'Las aguas termales son mejores al atardecer. Lleva repelente de insectos para las caminatas nocturnas.', altTip: 'El Puente Colgante Mistico ofrece vistas espectaculares del dosel del bosque.' },
  monteverde: { region: 'Monteverde', icon: '☁️', tip: 'Madruga (5:30am) para tener más probabilidad de ver el Quetzal. Lleva chaqueta impermeable.', altTip: 'El Night Walk es imperdible para ver ranas, insectos y mamíferos nocturnos.' },
  manuel: { region: 'Manuel Antonio', icon: '🦁', tip: 'El parque abre a las 6am. Llega temprano para evitar multitudes y ver más fauna.', altTip: 'Lleva binoculares para observar monos, perezosos y tucanes desde los senderos.' },
  caribe: { region: 'Caribe Sur', icon: '🌴', tip: 'Prueba el rondón (rondó) en Puerto Viejo. El chocolate artesanal de cacao orgánico es imperdible.', altTip: 'Alquila una bicicleta para recorrer la costa entre Puerto Viejo y Manzanillo.' },
  central: { region: 'Valle Central', icon: '🏛️', tip: 'El Mercado Central tiene la mejor comida típica. No dejes de probar un café de la Feria del Café.', altTip: 'Visita el Teatro Nacional, joya arquitectónica, y el Museo del Oro Precolombino.' }
}

const activityTemplates: Record<string, Record<string, any[]>> = {
  relax: {
    guanacaste: [
      { time: 'Mañana', desc: 'Desayuno frente al mar y caminata en la playa', detail: 'Prueba el gallo pinto con huevos', cost: 8 },
      { time: 'Media mañana', desc: 'Clase de surf o paddleboard', detail: 'Escuelas locales, $40-60/hora', cost: 45 },
      { time: 'Mediodía', desc: 'Almuerzo en restaurante frente a la playa', detail: 'Pescado fresco del día', cost: 15 },
      { time: 'Tarde', desc: 'Hamaca y libro junto al mar', detail: '', cost: 0 },
      { time: 'Atardecer', desc: 'Atardecer en Playa Conchal', detail: 'Uno de los mejores atardeceres del país', cost: 0 },
      { time: 'Noche', desc: 'Cena marina y cócteles', detail: 'Prueba el ceviche de corvina', cost: 25 }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Desayuno con vista al volcán', detail: 'Muchos hoteles tienen vistas espectaculares', cost: 6 },
      { time: 'Media mañana', desc: 'Visita a las aguas termales', detail: 'Tabacón o Baldi, $40-80 entrada', cost: 55 },
      { time: 'Mediodía', desc: 'Almuerzo en restaurante local', detail: 'Comida típica casada', cost: 12 },
      { time: 'Tarde', desc: 'Spa o masaje junto a las termales', detail: 'Muchos resorts ofrecen paquetes', cost: 60 },
      { time: 'Atardecer', desc: 'Cóctel con vista al volcán', detail: 'Si el clima lo permite, espectacular', cost: 10 },
      { time: 'Noche', desc: 'Cena romántica y observación de estrellas', detail: 'Cielos despejados ideales', cost: 30 }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Desayuno en la nube', detail: 'Café de altura, clima fresco', cost: 6 },
      { time: 'Media mañana', desc: 'Caminata suave por senderos del bosque', detail: 'Sendero Sendero Bosque Nuboso', cost: 0 },
      { time: 'Mediodía', desc: 'Almuerzo típico en Santa Elena', detail: 'Casado o arroz con pollo', cost: 10 },
      { time: 'Tarde', desc: 'Visita a reserva de colibríes', detail: 'Entrada $5, hay más de 14 especies', cost: 5 },
      { time: 'Atardecer', desc: 'Mirador del Golfo de Nicoya', detail: 'Vista impresionante', cost: 0 },
      { time: 'Noche', desc: 'Cena junto a la chimenea', detail: 'Clima fresco, ideal para vino', cost: 20 }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Desayuno con vista al océano', detail: '', cost: 8 },
      { time: 'Media mañana', desc: 'Tour guiado en Parque Nacional', detail: 'Guía local $40, entrada $18', cost: 50 },
      { time: 'Mediodía', desc: 'Picnic en Playa Espadilla', detail: '', cost: 10 },
      { time: 'Tarde', desc: 'Snorkel y natación en playa', detail: 'Aguas cristalinas, equipo $15', cost: 15 },
      { time: 'Atardecer', desc: 'Observación de monos en la playa', detail: 'Los monos capuchinos bajan al atardecer', cost: 0 },
      { time: 'Noche', desc: 'Cena de mariscos en el pueblo', detail: 'Prueba el arroz con camarones', cost: 20 }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Desayuno caribeño', detail: 'Pan bon, patí y café', cost: 6 },
      { time: 'Media mañana', desc: 'Snorkel en Playa Chiquita', detail: 'Arrecife cerca de la orilla', cost: 10 },
      { time: 'Mediodía', desc: 'Almuerzo de rondón', detail: 'Plato típico afrocaribeño', cost: 12 },
      { time: 'Tarde', desc: 'Bicicleta por la costa', detail: 'Alquiler $10/día', cost: 10 },
      { time: 'Atardecer', desc: 'Cerveza artesanal en la playa', detail: '', cost: 5 },
      { time: 'Noche', desc: 'Música reggae en vivo', detail: 'Bares locales con ambiente único', cost: 15 }
    ],
    central: [
      { time: 'Mañana', desc: 'Desayuno en el Mercado Central', detail: 'Comida típica, café chorreado', cost: 6 },
      { time: 'Media mañana', desc: 'Tour por el Teatro Nacional', detail: 'Joyacultural, entrada $12', cost: 12 },
      { time: 'Mediodía', desc: 'Almuerzo en Barrio Escalante', detail: 'Zona gastronómica de moda', cost: 15 },
      { time: 'Tarde', desc: 'Museo del Oro Precolombino', detail: 'Entrada $11, colección impresionante', cost: 11 },
      { time: 'Atardecer', desc: 'Café en la Feria del Café', detail: 'Prueba el café de altura', cost: 5 },
      { time: 'Noche', desc: 'Cena en restaurante gourmet', detail: 'Cocina fusión costarricense', cost: 30 }
    ]
  },
  adventure: {
    guanacaste: [
      { time: 'Mañana', desc: 'Surf en Playa Tamarindo o Langosta', detail: 'Clases desde $40, olas para todos los niveles', cost: 45 },
      { time: 'Media mañana', desc: 'Paseo en catamarán con snorkel', detail: 'Incluye bebidas y almuerzo, $80', cost: 70 },
      { time: 'Tarde', desc: 'ATV por senderos del bosque tropical seco', detail: 'Tour 3h, $90 por persona', cost: 80 },
      { time: 'Noche', desc: 'Cena y fiesta en Tamarindo', detail: 'Vida nocturna vibrante', cost: 25 }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Rafting en Río Pacuare (clase III-IV)', detail: 'Full day, almuerzo incluido, $95', cost: 85 },
      { time: 'Tarde', desc: 'Canyoning o rapel por cascadas', detail: '3h, equipo incluido, $70', cost: 65 },
      { time: 'Noche', desc: 'Safari nocturno en busca de fauna', detail: 'Guía experto, linternas, $40', cost: 35 }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Canopy tirolesa (14 cables, 2km+)', detail: 'Vuelo del halcón, $50', cost: 45 },
      { time: 'Tarde', desc: 'Puentes colgantes + rappel', detail: 'Recorrido por dosel, $55', cost: 50 },
      { time: 'Noche', desc: 'Night walk: ranas, insectos y mamíferos', detail: 'Guía especializado, $30', cost: 28 }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Tour guiado Parque Nacional + senderismo', detail: 'Guía bilingüe, 3-4h, $40+$18 entrada', cost: 50 },
      { time: 'Tarde', desc: 'Kayak en manglares', detail: '2h, $45 por persona', cost: 40 },
      { time: 'Noche', desc: 'Tour nocturno de fauna', detail: 'Guía con spotlight, $35', cost: 30 }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Snorkel en Parque Nacional Cahuita', detail: 'Arrecife coralino, entrada donación', cost: 10 },
      { time: 'Tarde', desc: 'Kayak en el Canal de Tortuguero', detail: 'Fauna acuática, $50', cost: 45 },
      { time: 'Noche', desc: 'Observación de tortugas (temporada)', detail: 'Jul-Oct, guía autorizado, $35', cost: 30 }
    ],
    central: [
      { time: 'Mañana', desc: 'Bike por el Bosque de la Hoja', detail: 'Ruta de montaña, $30 alquiler', cost: 25 },
      { time: 'Tarde', desc: 'Rapel en cascada en Bajos del Toro', detail: '1h de SJ, $65', cost: 60 },
      { time: 'Noche', desc: 'Escape room en San José', detail: 'Varias temáticas, $15/persona', cost: 12 }
    ]
  },
  nature: {
    guanacaste: [
      { time: 'Mañana', desc: 'Tour en Parque Nacional Rincón de la Vieja', detail: 'Senderismo, volcanes, aguas termales naturales', cost: 25 },
      { time: 'Tarde', desc: 'Avistamiento de aves en Palo Verde', detail: 'Más de 280 especies, tour en bote', cost: 45 },
      { time: 'Noche', desc: 'Observación de tortugas marinas', detail: 'Temporada adecuada, guía local', cost: 30 }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Senderismo Parque Nacional Volcán Arenal', detail: 'Sendero Coladas 1968, 3h', cost: 15 },
      { time: 'Tarde', desc: 'Reserva del Silencio: puentes colgantes', detail: 'Dosel del bosque, fauna variada', cost: 35 },
      { time: 'Noche', desc: 'Safari nocturno privado', detail: 'Guía naturalista, equipo óptico', cost: 40 }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Birdwatching del Quetzal (5:30am)', detail: 'Reserva Bosque Nuboso, $25, guía $35', cost: 55 },
      { time: 'Tarde', desc: 'Reserva Santa Elena: caminata autoguiada', detail: 'Senderos señalizados, $14', cost: 12 },
      { time: 'Noche', desc: 'Night walk: ranas venenosas e insectos', detail: 'Guía experto, $25', cost: 22 }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Tour naturalista en Parque Nacional', detail: 'Monos, perezosos, tucanes, iguanas', cost: 50 },
      { time: 'Tarde', desc: 'Sendero autoguiado Playa Espadilla Sur', detail: 'Manglares y vida silvestre', cost: 0 },
      { time: 'Noche', desc: 'Tour de insectos y anfibios nocturnos', detail: 'Guía especializado, linternas UV', cost: 30 }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Tour en el Parque Nacional Cahuita', detail: 'Sendero costero 8km, fauna diversa', cost: 8 },
      { time: 'Tarde', desc: 'Jardín Botánico y chocolates orgánicos', detail: 'Cacao tour, degustación, $20', cost: 18 },
      { time: 'Noche', desc: 'Tortugas marinas en Gandoca', detail: 'Desove de tortugas según temporada', cost: 25 }
    ],
    central: [
      { time: 'Mañana', desc: 'Jardín Botánico Lankester', detail: 'Orquídeas, bromelias, $12', cost: 10 },
      { time: 'Tarde', desc: 'Tour de café: Doka o Café Britt', detail: 'Recorrido plantación + degustación', cost: 35 },
      { time: 'Noche', desc: 'Poás o Irazú: volcán al atardecer', detail: '1h de SJ, cráteres activos', cost: 15 }
    ]
  },
  culture: {
    guanacaste: [
      { time: 'Mañana', desc: 'Clase de cocina típica guanacasteca', detail: 'Aprende a hacer gallo pinto, picadillo', cost: 40 },
      { time: 'Tarde', desc: 'Visita a la Hacienda de café boutique', detail: 'Café orgánico de altura, degustación', cost: 30 },
      { time: 'Noche', desc: 'Música folclórica y baile popular', detail: 'Marimba y bailes típicos', cost: 15 }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Taller de artesanías locales', detail: 'Cerámica o tallado en madera', cost: 25 },
      { time: 'Tarde', desc: 'Tour por plantación de piña orgánica', detail: 'La más grande de CR, degustación', cost: 20 },
      { time: 'Noche', desc: 'Charla sobre cultura rural tica', detail: 'Familias locales comparten historias', cost: 10 }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Tour de café artesanal y chocolate', detail: 'Cooperativa local, $30 degustación', cost: 28 },
      { time: 'Tarde', desc: 'Galería de arte local y mariposario', detail: 'Arte regional y especies nativas', cost: 12 },
      { time: 'Noche', desc: 'Charla sobre conservación del bosque', detail: 'Centro científico tropical', cost: 5 }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Taller de cerámica indígena', detail: 'Técnicas tradicionales Huetar', cost: 30 },
      { time: 'Tarde', desc: 'Tour de manglares y cultura pesquera', detail: 'Comunidad local de Quepos', cost: 25 },
      { time: 'Noche', desc: 'Clase de baile latino (salsa, merengue)', detail: 'Escuela de baile local, $15', cost: 12 }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Tour de cacao y cultura afrocaribeña', detail: 'Historia del chocolate, degustación, $25', cost: 22 },
      { time: 'Tarde', desc: 'Lección de reggae y percusión', detail: 'Música afrocaribeña tradicional', cost: 20 },
      { time: 'Noche', desc: 'Cena típica con música en vivo', detail: 'Rondón, rice & beans, música afro', cost: 18 }
    ],
    central: [
      { time: 'Mañana', desc: 'Tour arquitectónico San José', detail: 'Teatro Nacional, Correos, Jardín de Paz', cost: 15 },
      { time: 'Tarde', desc: 'Museo Nacional + Museo del Jade', detail: 'Historia precolombina, $11 cada uno', cost: 20 },
      { time: 'Noche', desc: 'Teatro Popular Melico Salazar', detail: 'Obras locales o conciertos', cost: 15 }
    ]
  },
  romance: {
    guanacaste: [
      { time: 'Mañana', desc: 'Desayuno en la cama con vista al mar', detail: 'Muchos resorts ofrecen este servicio', cost: 10 },
      { time: 'Tarde', desc: 'Paseo en velero privado al atardecer', detail: 'Champagne y snorkel incluido, $120', cost: 100 },
      { time: 'Noche', desc: 'Cena romántica en la playa', detail: 'Cena privada con velas y pie', cost: 60 }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Masaje para parejas en spa termal', detail: '1h, $120 por pareja', cost: 55 },
      { time: 'Tarde', desc: 'Aguas termales privadas', detail: 'Resort Tabacón o The Springs', cost: 65 },
      { time: 'Noche', desc: 'Cena con vista al volcán iluminado', detail: 'Espectáculo natural nocturno', cost: 45 }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Caminata privada por el bosque nuboso', detail: 'Guía privado para parejas, $60', cost: 50 },
      { time: 'Tarde', desc: 'Picnic en mirador secreto', detail: 'Vista al Golfo de Nicoya', cost: 15 },
      { time: 'Noche', desc: 'Cena junto a la chimenea con vino', detail: 'Clima fresco, ambiente íntimo', cost: 35 }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Snorkel privado en Playa Biesanz', detail: 'Pequña cala, turistas locales', cost: 10 },
      { time: 'Tarde', desc: 'Spa de parejas frente al mar', detail: 'Masajes, hidroterapia, $100', cost: 85 },
      { time: 'Noche', desc: 'Cena gourmet en resort boutique', detail: 'Cocina fusión, vistas al Pacífico', cost: 50 }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Desayuno en la cama con frutas tropicales', detail: '', cost: 8 },
      { time: 'Tarde', desc: 'Bicicleta tándem por la costa', detail: 'Ruta Puerto Viejo-Manizillo, 10km', cost: 12 },
      { time: 'Noche', desc: 'Cena a la luz de las velas en la playa', detail: 'Sonido del mar, música reggae suave', cost: 30 }
    ],
    central: [
      { time: 'Mañana', desc: 'Desayuno en café boutique colonial', detail: 'Barrio Amón, arquitectura histórica', cost: 10 },
      { time: 'Tarde', desc: 'Tour privado de café especial', detail: 'Degustación de microlotes, $40', cost: 35 },
      { time: 'Noche', desc: 'Cena en restaurante gourmet', detail: 'Top 10 Latinoamérica, cena maridaje', cost: 55 }
    ]
  },
  family: {
    guanacaste: [
      { time: 'Mañana', desc: 'Clase de surf para niños', detail: 'Olas suaves, instructores pacientes, $30', cost: 28 },
      { time: 'Tarde', desc: 'Paseo en barco con snorkel familiar', detail: 'Todos a bordo, incluye almuerzo', cost: 50 },
      { time: 'Noche', desc: 'Cena buffet temática en hotel', detail: 'Noche mexicana o típica', cost: 20 }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Puentes colgantes Mistico', detail: 'Seguro para niños, vistas increíbles', cost: 28 },
      { time: 'Tarde', desc: 'Aguas termales familiares', detail: 'Piscinas de diferentes temperaturas', cost: 35 },
      { time: 'Noche', desc: 'Chocolate tour: de la semilla a la tableta', detail: 'Degustación, divertido para niños', cost: 20 }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Reserva de colibríes y mariposario', detail: '14 especies de colibríes, $8', cost: 6 },
      { time: 'Tarde', desc: 'Canopy para niños (tirolesa suave)', detail: 'Supervisado, arnés especial, $25', cost: 22 },
      { time: 'Noche', desc: 'Night walk educativo para familias', detail: 'Guía con linternas, $20 por familia', cost: 15 }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Tour guiado amigable para niños', detail: 'Guías especializados en fauna infantil', cost: 40 },
      { time: 'Tarde', desc: 'Playa Espadilla: juegos y natación', detail: 'Olas suaves, socorristas', cost: 0 },
      { time: 'Noche', desc: 'Helado artesanal y paseo por el pueblo', detail: 'Sabores tropicales', cost: 8 }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Snorkel en aguas poco profundas', detail: 'Playa Chiquita, aguas calmadas', cost: 10 },
      { time: 'Tarde', desc: 'Rescatr: santuario de perezosos y monos', detail: 'Centro de rescate, educativo, $15', cost: 12 },
      { time: 'Noche', desc: 'Noche de juegos de mesa en el hotel', detail: 'Ambiente familiar relajado', cost: 0 }
    ],
    central: [
      { time: 'Mañana', desc: 'Museo de los Niños en San José', detail: 'Interactivo, educativo, $5', cost: 4 },
      { time: 'Tarde', desc: 'Parque Nacional Volcán Poás', detail: 'Crater accesible, 1h de SJ', cost: 15 },
      { time: 'Noche', desc: 'Cena temprana en soda familiar', detail: 'Comida típica, barata y buena', cost: 8 }
    ]
  }
}

const accommodationCosts: Record<string, number> = {
  budget: 35,
  mid: 90,
  premium: 220,
  luxury: 450
}

const foodCostPerDay: Record<string, number> = {
  budget: 20,
  mid: 35,
  premium: 60,
  luxury: 100
}

const transportCostData: Record<string, number> = {
  shuttle: 25,
  rental: 40,
  private: 70,
  public: 10
}

const generateItinerary = () => {
  const style = form.style || 'relax'
  const acc = form.accommodation || 'mid'
  const selectedDests = form.destinations.length > 0 ? form.destinations : ['guanacaste', 'arenal', 'monteverde']

  const itinerary: any[] = []

  const templates = activityTemplates[style]
  const days = durationDays.value
  const destsPerDay = Math.max(1, Math.floor(days / selectedDests.length))
  let dayIndex = 0
  let actCount = 0

  selectedDests.forEach((dest, dIdx) => {
    const isLast = dIdx === selectedDests.length - 1
    const destDays = isLast ? days - dayIndex : Math.min(destsPerDay, days - dayIndex)
    const destActivities = templates[dest] || templates[selectedDests[0]]

    for (let d = 0; d < destDays && dayIndex < days; d++) {
      dayIndex++
      const info = destInfo[dest]
      const roomCost = accommodationCosts[acc]
      const food = foodCostPerDay[acc]
      const transport = transportCostData[form.transport]

      const acts = destActivities ? [...destActivities] : [
        { time: 'Mañana', desc: 'Exploración libre del destino', detail: 'Descubre por tu cuenta', cost: 0 },
        { time: 'Tarde', desc: 'Almuerzo y tiempo libre', detail: '', cost: 10 },
        { time: 'Noche', desc: 'Cena y descanso', detail: '', cost: 15 }
      ]

      const actCost = acts.reduce((sum, a) => sum + (a.cost || 0), 0)
      const dayCost = roomCost + food + transport + actCost

      itinerary.push({
        title: dayIndex === 1 ? `Llegada a ${info.region}` : d === 0 ? `Explorando ${info.region}` : `Día en ${info.region}`,
        region: info.region,
        icon: info.icon,
        activities: acts,
        tip: d % 2 === 0 ? info.tip : info.altTip,
        dayCost,
        costs: { housing: roomCost, food, activities: actCost, transport }
      })

      actCount += acts.length
    }
  })

  totalActivities.value = actCount
  generatedItinerary.value = itinerary
  estimatedTotal.value = costBreakdown.value.housing + costBreakdown.value.food + costBreakdown.value.activities + costBreakdown.value.transport
}

const getActivityIcon = (index: number): string => {
  const icons = ['☀️', '🌤️', '🍽️', '🎯', '🌅', '🌙']
  return icons[index % icons.length]
}

const getActivityColor = (index: number): string => {
  const colors = ['bg-amber-100 text-amber-600', 'bg-yellow-100 text-yellow-600', 'bg-green-100 text-green-600', 'bg-blue-100 text-blue-600', 'bg-purple-100 text-purple-600', 'bg-indigo-100 text-indigo-600']
  return colors[index % colors.length]
}

const printItinerary = () => {
  window.print()
}

const copyItinerary = async () => {
  let text = '🗺️ ITINERARIO COSTA RICA\n'
  text += '='.repeat(30) + '\n\n'
  generatedItinerary.value.forEach((day, i) => {
    text += `📍 DÍA ${i + 1}: ${day.title}\n`
    text += `   Región: ${day.region}\n`
    day.activities.forEach((a: any) => {
      text += `   ${a.time}: ${a.desc}${a.cost ? ' ($' + a.cost + ')' : ''}\n`
    })
    text += `   💡 ${day.tip}\n`
    text += `   💰 Costo del día: $${day.dayCost}/persona\n\n`
  })
  text += '='.repeat(30) + '\n'
  text += `📊 Total estimado: $${estimatedTotal.value}/persona\n`
  text += `🗓️ Duración: ${durationDays.value} días\n`
  text += `📍 Destinos: ${form.destinations.length}\n`

  try {
    await navigator.clipboard.writeText(text)
    toast.success('✅ Itinerario copiado al portapapeles')
  } catch {
    toast.add('No se pudo copiar automáticamente', 'error')
  }
}

const shareItinerary = () => {
  if (navigator.share) {
    navigator.share({
      title: 'Mi itinerario en Costa Rica',
      text: `🌴 Viaje a Costa Rica: ${durationDays.value} días visitando ${form.destinations.length} destinos. Presupuesto: $${estimatedTotal.value}/persona.`,
      url: window.location.href
    }).catch(() => {})
  } else {
    copyItinerary()
  }
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const saveLead = async () => {
  try {
    const body = {
      duration: form.duration || '7-10',
      budget: form.budget,
      style: form.style || 'relax',
      destinations: form.destinations.length > 0 ? form.destinations : ['guanacaste'],
      travelers: form.travelers,
      season: form.season,
      transport: form.transport,
      accommodation: form.accommodation,
      notes: form.notes || null,
      estimated_cost: estimatedTotal.value,
      total_days: durationDays.value,
      itinerary: generatedItinerary.value.map((day: any) => ({
        title: day.title,
        region: day.region,
        icon: day.icon,
        activities: day.activities.map((a: any) => ({
          time: a.time,
          desc: a.desc,
          detail: a.detail || null,
          cost: a.cost || 0
        })),
        tip: day.tip,
        dayCost: day.dayCost,
        costs: day.costs
      }))
    }

    await Promise.allSettled([
      $fetch(`${apiBase}/planner/leads`, {
        method: 'POST',
        body,
        headers: { 'Content-Type': 'application/json' }
      }),
      $fetch(`${apiBase}/trip-planner/plans`, {
        method: 'POST',
        body: {
          name: `Viaje a Costa Rica - ${form.destinations.slice(0, 3).join(', ')}`,
          travelers: form.travelers,
          budget_min: Math.max(0, form.budget - 500),
          budget_max: form.budget + 500,
          notes: form.notes || `Plan generado por el planificador. Estilo: ${form.style}, Temporada: ${form.season}, Transporte: ${form.transport}`
        },
        headers: { 'Content-Type': 'application/json' }
      })
    ])

    toast.success('✅ Itinerario guardado exitosamente')
  } catch (e: any) {
    console.error('Failed to save lead:', e)
    toast.error('El itinerario se generó pero no se pudo guardar en el servidor')
  }
}

const resetPlanner = () => {
  currentStep.value = 1
  form.duration = null
  form.budget = 1500
  form.style = null
  form.destinations = []
  form.travelers = 2
  form.season = 'any'
  form.transport = 'shuttle'
  form.accommodation = 'mid'
  form.notes = ''
  generatedItinerary.value = []
  totalActivities.value = 0
  estimatedTotal.value = 0
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>
