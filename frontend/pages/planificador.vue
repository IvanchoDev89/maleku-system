<template>
  <div class="min-h-screen bg-gradient-to-br from-primary/5 to-accent/5 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <span class="text-primary font-semibold">{{ $t('planner.label') }}</span>
        <h1 class="text-4xl font-bold mt-2">{{ $t('planner.title') }}</h1>
        <p class="text-gray-600 mt-2">{{ $t('planner.subtitle') }}</p>
      </div>

      <!-- Progress Bar -->
      <div class="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <div class="flex justify-between items-center">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="flex items-center"
            :class="{ 'flex-1': index < steps.length - 1 }"
          >
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all"
              :class="currentStep > index + 1 ? 'bg-green-500 text-white' : currentStep === index + 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'"
            >
              <span v-if="currentStep > index + 1">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span 
              class="ml-2 text-sm hidden sm:block"
              :class="currentStep === index + 1 ? 'text-primary font-semibold' : 'text-gray-500'"
            >
              {{ step }}
            </span>
            <div v-if="index < steps.length - 1" class="flex-1 h-1 mx-4 bg-gray-200 rounded">
              <div 
                class="h-full bg-primary rounded transition-all"
                :style="{ width: currentStep > index + 1 ? '100%' : '0%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="bg-white rounded-2xl shadow-lg p-8">
        
        <!-- STEP 1: Duration -->
        <div v-show="currentStep === 1" class="space-y-6">
          <h2 class="text-2xl font-bold">{{ $t('step1.title') }}</h2>
          <p class="text-gray-600">{{ $t('step1.subtitle') }}</p>
          
          <div class="grid md:grid-cols-3 gap-4">
            <div 
              v-for="option in durationOptions" 
              :key="option.value"
              @click="form.duration = option.value"
              class="p-6 border-2 rounded-xl cursor-pointer transition-all text-center"
              :class="form.duration === option.value ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-primary/50'"
            >
              <div class="text-4xl mb-3">{{ option.icon }}</div>
              <h3 class="font-semibold text-lg">{{ option.label }}</h3>
              <p class="text-sm text-gray-500">{{ option.desc }}</p>
            </div>
          </div>

          <!-- Budget Slider -->
          <div class="mt-8 p-6 bg-gray-50 rounded-xl">
            <label class="block font-semibold mb-4">{{ $t('step1.budgetLabel') }}</label>
            <input 
              type="range" 
              v-model.number="form.budget"
              min="500" 
              max="10000" 
              step="100"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div class="flex justify-between mt-2 text-sm text-gray-500">
              <span>$500</span>
              <span class="text-primary font-bold text-lg">${{ form.budget.toLocaleString() }}</span>
              <span>$10,000</span>
            </div>
          </div>
        </div>

        <!-- STEP 2: Travel Style -->
        <div v-show="currentStep === 2" class="space-y-6">
          <h2 class="text-2xl font-bold">{{ $t('step2.title') }}</h2>
          <p class="text-gray-600">{{ $t('step2.subtitle') }}</p>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="option in styleOptions" 
              :key="option.value"
              @click="form.style = option.value"
              class="p-6 border-2 rounded-xl cursor-pointer transition-all"
              :class="form.style === option.value ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-primary/50'"
            >
              <div class="text-4xl mb-3">{{ option.icon }}</div>
              <h3 class="font-semibold text-lg">{{ option.label }}</h3>
              <p class="text-sm text-gray-500">{{ option.desc }}</p>
            </div>
          </div>
        </div>

        <!-- STEP 3: Destinations -->
        <div v-show="currentStep === 3" class="space-y-6">
          <h2 class="text-2xl font-bold">{{ $t('step3.title') }}</h2>
          <p class="text-gray-600">{{ $t('step3.subtitle') }}</p>

          <div class="grid md:grid-cols-2 gap-4">
            <div 
              v-for="dest in destinationOptions" 
              :key="dest.value"
              @click="toggleDestination(dest.value)"
              class="flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all"
              :class="form.destinations.includes(dest.value) ? 'border-primary bg-primary/5' : 'border-gray-200'"
            >
              <div class="text-3xl mr-4">{{ dest.icon }}</div>
              <div class="flex-1">
                <h3 class="font-semibold">{{ dest.label }}</h3>
                <p class="text-sm text-gray-500">{{ dest.desc }}</p>
              </div>
              <div 
                class="w-6 h-6 rounded-full flex items-center justify-center"
                :class="form.destinations.includes(dest.value) ? 'bg-primary text-white' : 'bg-gray-200'"
              >
                <span v-if="form.destinations.includes(dest.value)">✓</span>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 4: Details -->
        <div v-show="currentStep === 4" class="space-y-6">
          <h2 class="text-2xl font-bold">{{ $t('step4.title') }}</h2>
          <p class="text-gray-600">{{ $t('step4.subtitle') }}</p>

          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <label class="block font-semibold mb-2">{{ $t('step4.travelers') }}</label>
              <UiSelect v-model="form.travelers" :options="travelerOptions" />
            </div>
            <div>
              <label class="block font-semibold mb-2">{{ $t('step4.season') }}</label>
              <UiSelect v-model="form.season" :options="seasonOptions" />
            </div>
          </div>

          <div>
            <label class="block font-semibold mb-2">{{ $t('step4.notes') }}</label>
            <textarea 
              v-model="form.notes" 
              rows="3" 
              class="w-full p-3 border border-gray-200 rounded-lg"
              placeholder="Ej: Viajo con niños, soy摄影师, tengo limitaciones..."
            ></textarea>
          </div>

          <!-- Budget Summary -->
          <div class="p-6 bg-gradient-to-r from-primary to-primary-light rounded-xl text-white">
            <h3 class="font-bold text-lg mb-4">📊 {{ $t('budget.summary') }}</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm opacity-80">{{ $t('budget.perPerson') }}</p>
                <p class="text-2xl font-bold">${{ form.budget.toLocaleString() }}</p>
              </div>
              <div>
                <p class="text-sm opacity-80">{{ $t('budget.totalGroup') }}</p>
                <p class="text-2xl font-bold">${{ (form.budget * form.travelers).toLocaleString() }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- STEP 5: Result -->
        <div v-show="currentStep === 5" class="space-y-6">
          <div class="text-center mb-8">
            <div class="text-6xl mb-4">🎉</div>
            <h2 class="text-2xl font-bold">{{ $t('step5.title') }}</h2>
            <p class="text-gray-600">{{ $t('step5.subtitle') }}</p>
          </div>

          <!-- Itinerary Timeline -->
          <div class="relative">
            <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-primary"></div>
            
            <div 
              v-for="(day, index) in generatedItinerary" 
              :key="index"
              class="relative pl-20 pb-8"
            >
              <div class="absolute left-6 w-5 h-5 bg-primary rounded-full border-4 border-white"></div>
              
              <div class="bg-gray-50 rounded-xl p-6">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="font-bold text-lg">{{ day.title }}</h3>
                  <span class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                    {{ day.region }}
                  </span>
                </div>
                
                <div class="space-y-3">
                  <div 
                    v-for="activity in day.activities" 
                    :key="activity.time"
                    class="flex items-start gap-4"
                  >
                    <span class="text-primary font-semibold text-sm min-w-[80px]">
                      {{ activity.time }}
                    </span>
                    <span class="text-gray-700">{{ activity.desc }}</span>
                  </div>
                </div>

                <div class="mt-4 p-3 bg-accent/10 rounded-lg text-sm text-accent">
                  💡 {{ day.tip }}
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap justify-center gap-4">
            <button @click="printItinerary" class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2">
              🖨️ {{ $t('step5.print') }}
            </button>
            <button @click="shareItinerary" class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2">
              📤 Compartir
            </button>
            <button @click="resetPlanner" class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark flex items-center gap-2">
              🔄 {{ $t('step5.reset') }}
            </button>
          </div>
        </div>

        <!-- Navigation -->
        <div class="flex justify-between mt-8 pt-6 border-t">
          <button 
            v-if="currentStep > 1"
            @click="prevStep"
            class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
          >
            ← {{ $t('nav.prev') }}
          </button>
          <div v-else></div>

          <button 
            v-if="currentStep < 5"
            @click="nextStep"
            :disabled="!canProceed"
            class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {{ $t('nav.next') }} →
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

useSeo({
  title: 'Planificador de Viaje',
  description: 'Planifica tu viaje ideal a Costa Rica con nuestro planificador interactivo. Selecciona duración, estilo, destinos y genera tu itinerario personalizado.',
  keywords: 'planificador viaje Costa Rica, itinerary, itinerario, planificar viaje, ruta Costa Rica, viaje personalizado',
  ogType: 'website'
})

useJsonLd({
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Planificador de Viaje Costa Rica",
  "description": "Herramienta interactiva para planificar tu viaje a Costa Rica",
  "url": "https://costaricatravel.dev/planificador",
  "applicationCategory": "TravelApplication"
})

const currentStep = ref(1)
const steps = ['Duración', 'Estilo', 'Destinos', 'Detalles', 'Resultado']

const form = reactive({
  duration: null as string | null,
  budget: 1500,
  style: null as string | null,
  destinations: [] as string[],
  travelers: 2,
  season: 'any',
  notes: ''
})

const durationOptions = [
  { value: '3-5', icon: '🌟', label: 'Cortito', desc: '3-5 días - Ideal para una muestra' },
  { value: '7-10', icon: '⭐', label: 'Estándar', desc: '7-10 días - La duración perfecta' },
  { value: '14+', icon: '🏆', label: 'Extendido', desc: '14+ días - Explora a fondo' }
]

const styleOptions = [
  { value: 'relax', icon: '🏖️', label: 'Relax y Playa', desc: 'Sol, arena y descanso' },
  { value: 'adventure', icon: '🧗', label: 'Aventura', desc: 'Adrenalina y acción' },
  { value: 'nature', icon: '🌿', label: 'Naturaleza', desc: 'Fauna y ecosistemas' },
  { value: 'culture', icon: '🏛️', label: 'Cultura', desc: 'Historia y tradiciones' },
  { value: 'romance', icon: '💕', label: 'Romance', desc: 'Escapadas en pareja' },
  { value: 'family', icon: '👨‍👩‍👧', label: 'Familia', desc: 'Para toda la familia' }
]

const destinationOptions = [
  { value: 'guanacaste', icon: '🏖️', label: 'Guanacaste', desc: 'Playas doradas, surf' },
  { value: 'arenal', icon: '🌋', label: 'Arenal', desc: 'Volcán, termales' },
  { value: 'monteverde', icon: '☁️', label: 'Monteverde', desc: 'Bosque nuboso' },
  { value: 'manuel', icon: '🦁', label: 'Manuel Antonio', desc: 'Playa y vida salvaje' },
  { value: 'caribe', icon: '🌴', label: 'Caribe', desc: 'Cultura afrocaribeña' },
  { value: 'central', icon: '🏛️', label: 'Valle Central', desc: 'Ciudad y cafés' }
]

const canProceed = computed(() => {
  if (currentStep.value === 1) return form.duration !== null
  if (currentStep.value === 2) return form.style !== null
  if (currentStep.value === 3) return form.destinations.length > 0
  return true
})

const travelerOptions = [
  { value: 1, label: '1' },
  { value: 2, label: '2' },
  { value: 3, label: '3' },
  { value: 4, label: '4' },
  { value: 5, label: '5+' },
]

const seasonOptions = computed(() => [
  { value: 'any', label: t('step4.anyTime') },
  { value: 'dec-apr', label: t('step4.drySeason') },
  { value: 'may-nov', label: t('step4.rainySeason') },
])

const toggleDestination = (value: string) => {
  const index = form.destinations.indexOf(value)
  if (index > -1) {
    form.destinations.splice(index, 1)
  } else {
    form.destinations.push(value)
  }
}

const nextStep = () => {
  if (currentStep.value < 5) {
    currentStep.value++
    if (currentStep.value === 5) {
      generateItinerary()
    }
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const generatedItinerary = ref<any[]>([])

const generateItinerary = () => {
  const nights = form.duration === '3-5' ? 4 : form.duration === '7-10' ? 7 : 14
  const selectedDests = form.destinations.length > 0 ? form.destinations : ['guanacaste', 'arenal', 'monteverde']
  
  const destInfo: Record<string, any> = {
    guanacaste: { region: 'Guanacaste', icon: '🏖️', tip: 'No te pierdas el atardecer en Playa Conchal' },
    arenal: { region: 'Arenal', icon: '🌋', tip: 'Las termales son mejores al atardecer' },
    monteverde: { region: 'Monteverde', icon: '☁️', tip: 'Madruga para ver el quetzal' },
    manuel: { region: 'Manuel Antonio', icon: '🦁', tip: 'El parque abre a las 6am' },
    caribe: { region: 'Caribe', icon: '🌴', tip: 'Prueba el rondó en Puerto Viejo' },
    central: { region: 'Valle Central', icon: '🏛️', tip: 'El mercado central tiene la mejor comida' }
  }

  const activities: Record<string, any> = {
    guanacaste: [
      { time: 'Mañana', desc: 'Llegada y check-in' },
      { time: 'Mediodía', desc: 'Almuerzo en Tamarindo' },
      { time: 'Tarde', desc: 'Surf o relax en playa' },
      { time: 'Atardecer', desc: 'Coucher de soleil en Playa Conchal' }
    ],
    arenal: [
      { time: 'Mañana', desc: 'Senderismo en Parque Nacional' },
      { time: 'Mediodía', desc: 'Almuerzo con vista al volcán' },
      { time: 'Tarde', desc: 'Baños termales' },
      { time: 'Noche', desc: 'Safari nocturno' }
    ],
    monteverde: [
      { time: 'Mañana', desc: 'Caminata en bosque nuboso' },
      { time: 'Mediodía', desc: 'Almuerzo típico' },
      { time: 'Tarde', desc: 'Tirolesa en canopy' },
      { time: 'Noche', desc: 'Tour de fauna' }
    ],
    manuel: [
      { time: 'Mañana', desc: 'Tour en Parque Nacional' },
      { time: 'Mediodía', desc: 'Picnic en la playa' },
      { time: 'Tarde', desc: 'Snorkel en arrecife' },
      { time: 'Atardecer', desc: 'Observación de monos' }
    ],
    caribe: [
      { time: 'Mañana', desc: 'Exploración de Puerto Viejo' },
      { time: 'Mediodía', desc: 'Rondó (comida caribeña)' },
      { time: 'Tarde', desc: 'Snorkel en Cahuita' },
      { time: 'Noche', desc: 'Música y ambiente local' }
    ],
    central: [
      { time: 'Mañana', desc: 'Tour por San José' },
      { time: 'Mediodía', desc: 'Mercado Central' },
      { time: 'Tarde', desc: 'Museo Nacional' },
      { time: 'Tarde', desc: 'Tour de café' }
    ]
  }

  generatedItinerary.value = selectedDests.map((dest, index) => ({
    title: `Día ${index + 1}: ${destInfo[dest].region}`,
    region: destInfo[dest].region,
    activities: activities[dest],
    tip: destInfo[dest].tip
  }))
}

const printItinerary = () => {
  window.print()
}

const toast = useToast()

const shareItinerary = () => {
  toast.success('¡Comparte tu itinerario! (Integración de compartir coming soon)')
}

const resetPlanner = () => {
  currentStep.value = 1
  form.duration = null
  form.budget = 1500
  form.style = null
  form.destinations = []
  form.travelers = 2
  form.season = 'any'
  form.notes = ''
  generatedItinerary.value = []
}
</script>