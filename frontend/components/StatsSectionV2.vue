<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Stat {
  value: number
  suffix: string
  label: string
  icon: string
  description: string
}

const stats = ref<Stat[]>([
  { value: 6, suffix: '%', label: 'Biodiversidad Mundial', icon: '🦋', description: 'En solo el 0.03% del planeta' },
  { value: 500, suffix: 'K+', label: 'Especies', icon: '🌿', description: 'Flora y fauna por descubrir' },
  { value: 30, suffix: '+', label: 'Parques Nacionales', icon: '🏞️', description: 'Áreas protegidas' },
  { value: 300, suffix: '', label: 'Playas', icon: '🏖️', description: 'Pacífico y Caribe' },
  { value: 10000, suffix: '+', label: 'Viajeros', icon: '😊', description: 'Nos recomiendan' },
  { value: 98, suffix: '%', label: 'Satisfacción', icon: '⭐', description: 'Experiencias 5 estrellas' }
])

const animatedValues = ref<number[]>(stats.value.map(() => 0))
const hasAnimated = ref(false)
const sectionRef = ref<HTMLElement | null>(null)

let observer: IntersectionObserver | null = null

const animateCounters = () => {
  if (hasAnimated.value) return
  hasAnimated.value = true

  stats.value.forEach((stat, index) => {
    const duration = 2000
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
  if (sectionRef.value) observer.observe(sectionRef.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section
    ref="sectionRef"
    class="relative py-24 overflow-hidden bg-gradient-to-br from-gray-900 via-primary-950 to-emerald-950 dark:from-gray-950 dark:via-primary-950 dark:to-emerald-950"
  >
    <div class="absolute inset-0 opacity-[0.03]">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-400 rounded-full blur-3xl animate-pulse" />
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-400 rounded-full blur-3xl animate-pulse animation-delay-2000" />
    </div>

    <div class="container mx-auto px-4 relative z-10">
      <div class="text-center mb-16">
        <span class="inline-flex items-center gap-2 px-5 py-2 bg-white/10 backdrop-blur-sm text-emerald-300 font-semibold rounded-full text-sm border border-white/10 mb-6">
          <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          Costa Rica en Números
        </span>
        <h2 class="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 leading-tight">
          Un País, Universo de Vida
        </h2>
        <p class="text-lg text-white/70 max-w-xl mx-auto">
          Donde la naturaleza alcanza su máxima expresión
        </p>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div
          v-for="(stat, index) in stats"
          :key="stat.label"
          class="group"
        >
          <div class="relative bg-white/[0.06] backdrop-blur-sm rounded-2xl p-6 hover:bg-white/[0.1] transition-all duration-500 hover:-translate-y-1 hover:shadow-2xl border border-white/[0.05] h-full">
            <div class="text-3xl mb-3 group-hover:scale-110 transition-transform duration-500">{{ stat.icon }}</div>
            <div class="text-3xl md:text-4xl font-bold text-white mb-1 font-mono tracking-tight">
              {{ animatedValues[index] }}<span class="text-emerald-300">{{ stat.suffix }}</span>
            </div>
            <div class="text-white/80 text-sm font-medium mb-1">{{ stat.label }}</div>
            <div class="text-white/40 text-xs">{{ stat.description }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
