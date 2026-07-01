import { defineEventHandler, getRouterParam, proxyRequest, getRequestURL } from 'h3'

export default defineEventHandler(async (event) => {
  const slug = getRouterParam(event, 'slug') || ''
  const query = getRequestURL(event).search
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string || 'http://localhost:8000/api/v1').replace(/\/api\/v1\/?$/, '/api')
  const target = `${apiBase}/${slug}${query}`
  return proxyRequest(event, target)
})
