export default defineEventHandler(async (event) => {
  const baseUrl = 'https://costaricatravel.dev'

  const staticPages = [
    { loc: '/', changefreq: 'daily', priority: 1.0 },
    { loc: '/destinos', changefreq: 'weekly', priority: 0.8 },
    { loc: '/hoteles', changefreq: 'weekly', priority: 0.8 },
    { loc: '/tours', changefreq: 'weekly', priority: 0.8 },
    { loc: '/blog', changefreq: 'weekly', priority: 0.7 },
    { loc: '/planificador', changefreq: 'monthly', priority: 0.6 },
    { loc: '/paquetes', changefreq: 'weekly', priority: 0.5 },
    { loc: '/login', changefreq: 'monthly', priority: 0.3 },
    { loc: '/register', changefreq: 'monthly', priority: 0.3 },
    { loc: '/vendor/register', changefreq: 'monthly', priority: 0.3 },
    { loc: '/faq', changefreq: 'monthly', priority: 0.3 },
    { loc: '/contacto', changefreq: 'monthly', priority: 0.3 },
    { loc: '/privacidad', changefreq: 'monthly', priority: 0.2 },
    { loc: '/terminos', changefreq: 'monthly', priority: 0.2 },
    { loc: '/search', changefreq: 'monthly', priority: 0.3 },
  ]

  let dynamicPages: { loc: string; changefreq: string; priority: number }[] = []

  try {
    const { public: { apiBase } } = useRuntimeConfig()
    const apiUrl = (apiBase as string || '').replace(/\/api\/v1$/, '')

    if (apiUrl) {
      const [destinations, properties, tours, blogPosts] = await Promise.all([
        $fetch<{ items: { slug: string }[] }>(`${apiUrl}/api/v1/destinations?page_size=100`).catch(() => null),
        $fetch<{ items: { slug: string }[] }>(`${apiUrl}/api/v1/properties?page_size=100`).catch(() => null),
        $fetch<{ items: { slug: string }[] }>(`${apiUrl}/api/v1/tours?page_size=100`).catch(() => null),
        $fetch<{ items: { slug: string }[] }>(`${apiUrl}/api/v1/blog?page_size=100&status=published`).catch(() => null),
      ])

      if (destinations?.items) {
        dynamicPages.push(...destinations.items.map(d => ({
          loc: `/destinos/${d.slug}`,
          changefreq: 'weekly' as const,
          priority: 0.8
        })))
      }
      if (properties?.items) {
        dynamicPages.push(...properties.items.map(p => ({
          loc: `/hoteles/${p.slug}`,
          changefreq: 'weekly' as const,
          priority: 0.7
        })))
      }
      if (tours?.items) {
        dynamicPages.push(...tours.items.map(t => ({
          loc: `/tours/${t.slug}`,
          changefreq: 'weekly' as const,
          priority: 0.7
        })))
      }
      if (blogPosts?.items) {
        dynamicPages.push(...blogPosts.items.map(b => ({
          loc: `/blog/${b.slug}`,
          changefreq: 'monthly' as const,
          priority: 0.6
        })))
      }
    }
  } catch {
    // API unavailable — fall back to static pages only
  }

  const allPages = [...staticPages, ...dynamicPages]

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
         xmlns:xhtml="http://www.w3.org/1999/xhtml">
  ${allPages.map(page => `  <url>
    <loc>${baseUrl}${page.loc}</loc>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
    <xhtml:link rel="alternate" hreflang="es" href="${baseUrl}${page.loc}"/>
    <xhtml:link rel="alternate" hreflang="en" href="${baseUrl}/en${page.loc}"/>
    <xhtml:link rel="alternate" hreflang="fr" href="${baseUrl}/fr${page.loc}"/>
  </url>`).join('\n')}
</urlset>`

  event.node.res.setHeader('content-type', 'application/xml')
  return sitemap
})
