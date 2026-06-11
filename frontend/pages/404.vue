<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-emerald-50">
    <div class="text-center px-6">
      <div class="text-9xl font-black text-primary-600/20 mb-4">404</div>
      <h1 class="text-4xl font-bold text-gray-900 mb-3">Página no encontrada</h1>
      <p class="text-lg text-gray-600 mb-8 max-w-md mx-auto">
        La página que buscas no existe o ha sido movida.
      </p>
      <div class="flex items-center justify-center gap-4">
        <NuxtLink to="/" class="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors">
          Volver al inicio
        </NuxtLink>
        <NuxtLink to="/destinos" class="px-6 py-3 bg-white text-primary-600 rounded-xl font-medium border border-primary-200 hover:bg-primary-50 transition-colors">
          Explorar destinos
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
