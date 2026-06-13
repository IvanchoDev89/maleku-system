<template>
  <div class="min-h-screen flex bg-gray-50">
    <!-- Skip to main content -->
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <!-- Left Panel - Visual (only on large screens) -->
    <div class="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-primary-600 via-primary-700 to-emerald-700 overflow-hidden">
      <!-- Background Image -->
      <div class="absolute inset-0">
        <NuxtImg
          src="https://images.unsplash.com/photo-1518638150340-f706e86654de?w=1200&q=85"
          alt="Costa Rica"
          class="w-full h-full object-cover opacity-30"
          width="1200"
          height="800"
          format="webp"
        />
      </div>

      <!-- Gradient Overlay -->
      <div class="absolute inset-0 bg-gradient-to-br from-primary-900/90 via-primary-800/70 to-emerald-900/80"></div>

      <!-- Decorative Elements -->
      <div class="absolute top-20 left-20 w-64 h-64 bg-primary-400/20 rounded-full blur-3xl"></div>
      <div class="absolute bottom-32 right-20 w-80 h-80 bg-emerald-400/20 rounded-full blur-3xl"></div>

      <slot name="left-panel">
        <!-- Content -->
        <div class="relative z-10 flex flex-col justify-center px-16 py-12 text-white">
          <!-- Logo -->
          <div class="mb-12">
            <div class="flex items-center gap-4 mb-8">
              <div class="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-xl border border-white/30">
                <span class="text-4xl">🌴</span>
              </div>
              <div>
                <h1 class="text-3xl font-bold">Costa Rica Travel</h1>
                <p class="text-primary-200">Tu aventura comienza aquí</p>
              </div>
            </div>
          </div>

          <!-- Features List -->
          <div class="space-y-6">
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
                <CheckCircle class="w-6 h-6 text-primary-300" />
              </div>
              <div>
                <h3 class="font-semibold text-lg">Más de 500 destinos únicos</h3>
                <p class="text-primary-200 text-sm">Desde playas paradisíacas hasta volcanes activos</p>
              </div>
            </div>

            <div class="flex items-start gap-4">
              <div class="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
                <Shield class="w-6 h-6 text-primary-300" />
              </div>
              <div>
                <h3 class="font-semibold text-lg">Reservas 100% seguras</h3>
                <p class="text-primary-200 text-sm">Pago protegido y cancelación gratis</p>
              </div>
            </div>

            <div class="flex items-start gap-4">
              <div class="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
                <Star class="w-6 h-6 text-primary-300" />
              </div>
              <div>
                <h3 class="font-semibold text-lg"> +10,000 viajeros satisfechos</h3>
                <p class="text-primary-200 text-sm">Reseñas verificadas de experiencias reales</p>
              </div>
            </div>
          </div>

          <!-- Stats -->
          <div class="mt-12 grid grid-cols-3 gap-6">
            <div class="text-center">
              <p class="text-4xl font-bold text-white">500+</p>
              <p class="text-primary-200 text-sm">Destinos</p>
            </div>
            <div class="text-center">
              <p class="text-4xl font-bold text-white">200+</p>
              <p class="text-primary-200 text-sm">Hoteles</p>
            </div>
            <div class="text-center">
              <p class="text-4xl font-bold text-white">98%</p>
              <p class="text-primary-200 text-sm">Satisfacción</p>
            </div>
          </div>
        </div>
      </slot>
    </div>

    <!-- Right Panel - Form -->
    <main id="main-content" class="w-full lg:w-1/2 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <!-- Mobile Logo -->
        <div class="lg:hidden text-center mb-8">
          <NuxtLink to="/" class="inline-flex items-center gap-2">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-emerald-600 rounded-xl flex items-center justify-center">
              <span class="text-2xl">🌴</span>
            </div>
            <span class="text-2xl font-bold text-primary-600">Costa Rica Travel</span>
          </NuxtLink>
        </div>

        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { CheckCircle, Shield, Star } from 'lucide-vue-next'
</script>
