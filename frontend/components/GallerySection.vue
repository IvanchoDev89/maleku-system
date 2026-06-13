<script setup lang="ts">
/**
 * Gallery Section
 * Masonry gallery de fotos de Costa Rica
 */
const galleryImages = [
  { src: 'https://images.unsplash.com/photo-1518638150340-f706e86654de?w=600&q=80', alt: 'Selva tropical', span: 'row-span-2' },
  { src: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=600&q=80', alt: 'Playa', span: '' },
  { src: 'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=600&q=80', alt: 'Volcán', span: '' },
  { src: 'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=600&q=80', alt: 'Fauna', span: 'row-span-2' },
  { src: 'https://images.unsplash.com/photo-1518457607834-6e8d80c183c5?w=600&q=80', alt: 'Aventura', span: '' },
  { src: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=600&q=80', alt: 'Caribe', span: '' }
]
</script>

<template>
  <section class="py-20 bg-white">
    <div class="container mx-auto px-4">
      <!-- Header -->
      <div class="text-center mb-12">
        <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-600 font-semibold rounded-full text-sm mb-4">
          📸 #CostaRicaTravel
        </span>
        <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Momentos Inolvidables
        </h2>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          Comparte tus aventuras con nosotros y descubre las experiencias de otros viajeros.
        </p>
      </div>

      <!-- Masonry Grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-[200px]">
        <div
          v-for="(image, index) in galleryImages"
          :key="index"
          :class="['relative overflow-hidden rounded-2xl group cursor-pointer', image.span]"
        >
          <NuxtImg
            :src="image.src"
            :alt="image.alt"
            class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            width="600"
            height="400"
            format="webp"
            loading="lazy"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="absolute bottom-4 left-4 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <span class="text-sm font-medium">{{ image.alt }}</span>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="text-center mt-12">
        <a
          href="https://instagram.com/costaricatravel"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-400 text-white font-bold rounded-full hover:shadow-lg transition-all"
        >
          <span>📷</span>
          Síguenos en Instagram
        </a>
      </div>
    </div>
  </section>
</template>
