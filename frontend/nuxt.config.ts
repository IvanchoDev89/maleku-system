export default defineNuxtConfig({
  devtools: { enabled: false },

  experimental: {
    appManifest: false
  },

  modules: [
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/i18n',
    '@nuxt/image',
    '@nuxtjs/color-mode',
    '@nuxt/icon',
  ],

  css: ['~/assets/css/main.css', '~/assets/css/a11y.css'],

  postcss: {
    plugins: {
      tailwindcss: {},
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_URL || '/api/v1',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://costaricatravel.dev',
      cdnUrl: process.env.NUXT_PUBLIC_CDN_URL || '',
      siteName: 'Costa Rica Travel',
      siteDescription: 'Descubre Costa Rica: playas, volcanes, selvas y aventuras únicas. Hoteles, tours y planificador de viajes interactivo.',
      siteTitleTemplate: '%s - Costa Rica Travel',
      sentryDsn: process.env.NUXT_PUBLIC_SENTRY_DSN || '',
      stripeKey: process.env.NUXT_PUBLIC_STRIPE_KEY || '',
      siteKeywords: process.env.NUXT_PUBLIC_SITE_KEYWORDS || 'Costa Rica, viaje, turismo, hoteles, tours, Playa, Volcán',
      environment: process.env.NUXT_PUBLIC_ENVIRONMENT || 'production'
    }
  },

  app: {
    pageTransition: { name: 'page', mode: 'out-in' },
    layoutTransition: { name: 'layout', mode: 'out-in' },
    head: {
      htmlAttrs: {
        dir: 'ltr'
      },
      meta: [
        { name: 'description', content: 'Costa Rica Travel - Tu guía completa para descubrir Costa Rica: hoteles, tours, destinos y planificador de viajes interactivo.' },
        { name: 'keywords', content: 'Costa Rica, viaje, turismo, hoteles, tours, Playa, Volcán, Arenal, Monteverde, Guanacaste, Manuel Antonio, ecoturismo, aventura' },
        { name: 'author', content: 'Costa Rica Travel' },
        { name: 'robots', content: 'index, follow, max-image-preview:large' },
        { property: 'og:locale', content: 'es_ES' },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: 'Costa Rica Travel' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:site', content: '@costaricatravel' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'dns-prefetch', href: 'https://fonts.googleapis.com' }
      ]
    }
  },

  i18n: {
    locales: [
      { code: 'es', name: 'Español', language: 'es-CR', file: 'es.json' },
      { code: 'en', name: 'English', language: 'en-US', file: 'en.json' },
      { code: 'fr', name: 'Français', language: 'fr-FR', file: 'fr.json' }
    ],
    defaultLocale: 'es',
    langDir: 'i18n/',
    strategy: 'prefix_except_default',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
      fallbackLocale: 'es'
    },
    // Prevenir hydration mismatches
    skipSettingLocaleOnNavigate: false
  },

  nitro: {
    preset: 'node-server',
    devProxy: {
      '/api': {
        target: 'http://localhost:8000/api',
        changeOrigin: true
      }
    },
    // SECURITY: Add security headers
    routeRules: {
      '/checkout/success': { redirect: '/confirmacion' },
      '/**': {
        headers: {
          'X-Frame-Options': 'DENY',
          'X-Content-Type-Options': 'nosniff',
          'Referrer-Policy': 'strict-origin-when-cross-origin',
          'Permissions-Policy': 'camera=(), microphone=(), geolocation=(self), payment=()',
          'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
        }
      }
    }
  },

  compatibilityDate: '2024-01-01',

  colorMode: {
    classSuffix: '',
    preference: 'system',
    fallback: 'light',
    storageKey: 'color-mode'
  },

  image: {
    domains: ['images.unsplash.com', 'picsum.photos', 'randomuser.me', 'res.cloudinary.com'],
    quality: 80,
    format: ['webp', 'jpg']
  },

  icon: {
    provider: 'server',
    mode: 'svg'
  },

  vite: {
    optimizeDeps: {
      include: ['nuxt/app']
    }
  }
})
