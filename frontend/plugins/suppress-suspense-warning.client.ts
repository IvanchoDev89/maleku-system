export default defineNuxtPlugin((nuxtApp) => {
  const originalWarnHandler = nuxtApp.vueApp.config.warnHandler
  nuxtApp.vueApp.config.warnHandler = (msg, instance, trace) => {
    if (typeof msg === 'string' && msg.includes('<Suspense>')) return
    if (originalWarnHandler) {
      originalWarnHandler(msg, instance, trace)
    } else {
      console.warn(msg, instance, trace)
    }
  }
})
