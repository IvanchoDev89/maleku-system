import * as Sentry from '@sentry/vue'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const dsn = config.public.sentryDsn

  if (!dsn) return

  Sentry.init({
    app: nuxtApp.vueApp,
    dsn,
    environment: config.public.environment || 'production',
    tracesSampleRate: 0.1,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  })

  nuxtApp.hook('vue:error', (error) => {
    Sentry.captureException(error)
  })
})
