import { useHead, useRuntimeConfig } from '#imports'

interface SeoMeta {
  title?: string
  description?: string
  keywords?: string
  ogImage?: string
  ogType?: string
  canonical?: string
  noindex?: boolean
}

// Default SEO config (should match backend settings)
const DEFAULT_SEO = {
  siteName: 'Costa Rica Travel',
  defaultDescription: 'Descubre Costa Rica: playas, volcanes, selvas y aventuras únicas. Hoteles, tours y planificador de viajes interactivo.',
  defaultKeywords: 'Costa Rica, viaje, turismo, hoteles, tours, Playa, Volcán'
}

export const useSeo = (meta: SeoMeta) => {
  const config = useRuntimeConfig()
  
  // Use runtime config if available, otherwise use defaults
  const siteName = config.public.siteName || DEFAULT_SEO.siteName
  const defaultDescription = config.public.siteDescription || DEFAULT_SEO.defaultDescription
  const defaultKeywords = (config.public as any).siteKeywords || DEFAULT_SEO.defaultKeywords
  
  const fullTitle = meta.title ? `${meta.title} - ${siteName}` : siteName
  const description = meta.description || defaultDescription
  const keywords = meta.keywords || defaultKeywords
  
  useHead({
    title: fullTitle,
    meta: [
      { name: 'description', content: description },
      { name: 'keywords', content: keywords },
      { name: 'robots', content: meta.noindex ? 'noindex, nofollow' : 'index, follow' },
      
      // Open Graph
      { property: 'og:title', content: fullTitle },
      { property: 'og:description', content: description },
      { property: 'og:image', content: meta.ogImage || '/og-default.svg' },
      { property: 'og:type', content: meta.ogType || 'website' },
      { property: 'og:url', content: meta.canonical || config.public.siteUrl },
      
      // Twitter
      { name: 'twitter:title', content: fullTitle },
      { name: 'twitter:description', content: description },
      { name: 'twitter:image', content: meta.ogImage || '/og-default.svg' },
      { name: 'twitter:card', content: 'summary_large_image' },
      
    ],
    link: [
      { rel: 'canonical', href: meta.canonical || config.public.siteUrl }
    ]
  })
}

export const useJsonLd = (schema: object) => {
  useHead({
    script: [
      {
        type: 'application/ld+json',
        children: JSON.stringify(schema)
      }
    ]
  })
}