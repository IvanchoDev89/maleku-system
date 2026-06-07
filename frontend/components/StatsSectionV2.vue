<script setup lang="ts">
/**
 * Stats Section V2
 * Estadísticas con counter animation
 */
import { ref, onMounted, onUnmounted } from 'vue'

interface Stat {
  value: number
  suffix: string
  label: string
  icon: string
}

const stats = ref<Stat[]>([
  { value: 5, suffix: '%', label: 'Biodiversidad Mundial', icon: '🌿' },
  { value: 500, suffix: 'K+', label: 'Especies', icon: '🦋' },
  { value: 30, suffix: '+', label: 'Parques Nacionales', icon: '🏞️' },
  { value: 300, suffix: '', label: 'Playas', icon: '🏖️' },
  { value: 10000, suffix: '+', label: 'Viajeros Felices', icon: '😊' },
  { value: 98, suffix: '%', label: 'Satisfacción', icon: '⭐' }
])

const animatedValues = ref<number[]>(stats.value.map(() => 0))
const hasAnimated = ref(false)
const sectionRef = ref<HTMLElement | null>(null)

let observer: IntersectionObserver | null = null

const animateCounters = () => {
  if (hasAnimated.value) return
  hasAnimated.value = true

  stats.value.forEach((stat, index) => {
    const duration = 2000 // 2 seconds
    const steps = 60
    const stepValue = stat.value / steps
    let currentStep = 0

    const interval = setInterval(() => {
      currentStep++
      animatedValues.value[index] = Math.round(stepValue * currentStep)

      if (currentStep >= steps) {
        animatedValues.value[index] = stat.value
        clearInterval(interval)
      }
    }, duration / steps)
  })
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounters()
          observer?.disconnect()
        }
      })
    },
    { threshold: 0.3 }
  )

  if (sectionRef.value) {
    observer.observe(sectionRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section 
    ref="sectionRef"
    class="py-20 bg-gradient-to-r from-primary-600 via-primary-500 to-accent-500 relative overflow-hidden"
  >
    <!-- Background Pattern -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute inset-0 bg-white/5"></div>
    </div>

    <div class="container mx-auto px-4 relative z-10">
      <!-- Section Header -->
      <div class="text-center mb-12">
        <span class="inline-block px-4 py-1.5 bg-white/20 text-white font-semibold rounded-full text-sm mb-4">
          Costa Rica en Números
        </span>
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-2">
          Un Pequeño País, Un Gran Mundo
        </h2>
        <p class="text-white/80 max-w-2xl mx-auto">
          Descubre por qué Costa Rica es el destino favorito de viajeros de todo el mundo
        </p>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 text-center">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.label"
          class="group"
        >
          <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105 hover:shadow-2xl">
            <div class="text-4xl mb-3">{{ stat.icon }}</div>
            <div class="text-4xl md:text-5xl font-bold text-white mb-2">
              {{ animatedValues[index] }}{{ stat.suffix }}
            </div>
            <div class="text-white/80 text-sm">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
