export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()

  const health = {
    status: 'ok',
    service: 'Costa Rica Travel Frontend',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage().rss,
  }

  try {
    const apiHealth = await $fetch<{ status: string }>(`${config.public.apiBase}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    })
    return {
      ...health,
      api: apiHealth.status,
    }
  } catch {
    return {
      ...health,
      api: 'unreachable',
    }
  }
})
