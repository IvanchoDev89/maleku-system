export default defineNuxtConfig({
  devtools: { enabled: false },
  
  modules: [
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/i18n',
    '@nuxt/image',
    '@nuxtjs/color-mode',
    '@nuxt/content',
    '@nuxt/icon'
  ],
  
  css: ['~/assets/css/main.css', '~/assets/css/a11y.css'],
  
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
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
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'dns-prefetch', href: 'https://fonts.googleapis.com' }
      ]
    }
  },
  
  // Alias para resolución de tipos
  alias: {
    '~/types': './types/index.ts'
  },
  
  i18n: {
    locales: [
      { code: 'es', name: 'Español', language: 'es-CR', file: 'es.json' },
      { code: 'en', name: 'English', language: 'en-US', file: 'en.json' },
      { code: 'fr', name: 'Français', language: 'fr-FR', file: 'fr.json' }
    ],
    defaultLocale: 'es',
    lazy: true,
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
    // SECURITY: Add security headers
    routeRules: {
      '/**': {
        headers: {
          'X-Frame-Options': 'DENY',
          'X-Content-Type-Options': 'nosniff',
          'Referrer-Policy': 'strict-origin-when-cross-origin',
          'Permissions-Policy': 'camera=(), microphone=(), geolocation=(self), payment=()',
          'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
          'X-XSS-Protection': '1; mode=block',
          'Content-Security-Policy': [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://js.stripe.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "media-src 'self' https:",
            "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 ws://localhost:4000 https://api.costaricatravel.dev https://api.stripe.com https://*.sentry.io https://api.cloudinary.com https://res.cloudinary.com",
            "frame-src 'self' https://*.stripe.com https://js.stripe.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
          ].join('; ')
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
  }
})