import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    environment: 'happy-dom',
    include: ['tests/unit/**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      include: ['composables/', 'stores/'],
    },
  },
})
