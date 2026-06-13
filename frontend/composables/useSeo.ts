import { useHead, useRuntimeConfig } from '#imports'
import { unref } from 'vue'
import type { MaybeRef } from 'vue'

interface SeoMeta {
  title?: MaybeRef<string>
  description?: MaybeRef<string>
  keywords?: MaybeRef<string>
  ogImage?: MaybeRef<string>
  ogType?: MaybeRef<string>
  canonical?: MaybeRef<string>
  noindex?: MaybeRef<boolean>
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

  const fullTitle = unref(meta.title) ? `${unref(meta.title)} - ${siteName}` : siteName
  const description = unref(meta.description) || defaultDescription
  const keywords = unref(meta.keywords) || defaultKeywords

  useHead({
    title: fullTitle,
    meta: [
      { name: 'description', content: description },
      { name: 'keywords', content: keywords },
      { name: 'robots', content: unref(meta.noindex) ? 'noindex, nofollow' : 'index, follow' },

      // Open Graph
      { property: 'og:title', content: fullTitle },
      { property: 'og:description', content: description },
      { property: 'og:image', content: unref(meta.ogImage) || '/og-default.svg' },
      { property: 'og:type', content: unref(meta.ogType) || 'website' },
      { property: 'og:url', content: unref(meta.canonical) || config.public.siteUrl },

      // Twitter
      { name: 'twitter:title', content: fullTitle },
      { name: 'twitter:description', content: description },
      { name: 'twitter:image', content: unref(meta.ogImage) || '/og-default.svg' },
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
