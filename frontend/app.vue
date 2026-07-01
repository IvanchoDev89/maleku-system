<template>
  <NuxtLayout>
    <NuxtPage />
    <UiToast />
  </NuxtLayout>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const colorMode = useColorMode()

const htmlAttrs = computed(() => ({
  lang: locale.value
}))

const colorScheme = computed(() =>
  colorMode.value === 'dark' ? 'dark' : 'light'
)

useHead({
  htmlAttrs,
  titleTemplate: (titleChunk) => {
    return titleChunk ? `${titleChunk} - Costa Rica Travel` : 'Costa Rica Travel'
  },
  link: [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap' }
  ],
  meta: [
    { charset: 'utf-8' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=5' },
    { name: 'theme-color', content: '#0D9488' },
    { name: 'color-scheme', content: colorScheme }
  ]
})
</script>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.layout-enter-active,
.layout-leave-active {
  transition: opacity 0.2s ease;
}
.layout-enter-from,
.layout-leave-to {
  opacity: 0;
}
</style>
