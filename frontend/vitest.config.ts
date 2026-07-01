import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    environment: 'happy-dom',
    include: ['tests/unit/**/*.spec.ts'],
    setupFiles: ['tests/unit/setup.ts'],
    globalSetup: 'tests/unit/global-setup.ts',
    server: {
      deps: {
        inline: ['@nuxt/test-utils'],
      },
    },
    coverage: {
      provider: 'v8',
      include: ['composables/', 'stores/'],
    },
  },
})
