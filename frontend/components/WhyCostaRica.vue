<template>
  <section class="py-24 bg-white">
    <div class="container mx-auto px-4">
      <div class="grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <span class="inline-block px-4 py-1.5 bg-primary-100 text-primary-600 font-semibold rounded-full text-sm mb-4">
            {{ $t('why.badge') }}
          </span>
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">{{ $t('why.title') }}</h2>
          <p class="text-lg text-gray-600 mb-8">{{ $t('why.subtitle') }}</p>

          <div class="space-y-4">
            <div v-for="(item, index) in features" :key="index" class="flex items-start gap-4">
              <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-xl">{{ item.icon }}</span>
              </div>
              <div>
                <h4 class="font-bold text-gray-900 mb-1">{{ item.title }}</h4>
                <p class="text-gray-600 text-sm">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="relative">
          <NuxtImg
            src="https://images.unsplash.com/photo-1519823551278-64ac92734fb1?w=600&q=80"
            alt="Costa Rica sloth"
            class="rounded-2xl shadow-2xl w-full"
            width="600"
            height="400"
            format="webp"
            loading="lazy"
          />
          <div class="absolute -bottom-6 -right-6 bg-primary-600 text-white p-6 rounded-2xl shadow-xl max-w-xs">
            <div class="text-3xl font-bold mb-1">28</div>
            <div class="text-sm opacity-90">{{ t('why.protected') }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const features = computed(() => [
  {
    icon: '🌿',
    title: t('why.features.biodiversity.title'),
    description: t('why.features.biodiversity.description')
  },
  {
    icon: '🛡️',
    title: t('why.features.safe.title'),
    description: t('why.features.safe.description')
  },
  {
    icon: '♻️',
    title: t('why.features.sustainability.title'),
    description: t('why.features.sustainability.description')
  },
  {
    icon: '🏔️',
    title: t('why.features.climate.title'),
    description: t('why.features.climate.description')
  }
])
</script>
