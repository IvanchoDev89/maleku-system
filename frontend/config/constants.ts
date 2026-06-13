/**
 * Centralized Constants Configuration
 * All hardcoded values from components and composables should be defined here
 */

// ============================================
// Destination Configuration
// ============================================
export const DESTINATIONS = {
  list: [
    { slug: 'guanacaste', key: 'guanacaste' },
    { slug: 'la-fortuna', key: 'fortuna' },
    { slug: 'monteverde', key: 'monteverde' },
    { slug: 'manuel-antonio', key: 'manuelantonio' },
    { slug: 'caribe', key: 'caribe' },
    { slug: 'valle-central', key: 'vallecentral' }
  ] as const,

  // Slugs for footer display (ordered)
  footerSlugs: ['guanacaste', 'fortuna', 'monteverde', 'manuelantonio'] as const
}

// ============================================
// Service Categories
// ============================================
export const SERVICES = {
  list: [
    { key: 'hotels', icon: '🏨' },
    { key: 'tours', icon: '🗺️' },
    { key: 'flights', icon: '✈️' },
    { key: 'packages', icon: '📦' }
  ] as const,

  // Keys for footer display
  footerKeys: ['hotels', 'tours', 'flights', 'packages'] as const
}

// ============================================
// Tour Categories with Icons
// ============================================
export const TOUR_CATEGORIES = [
  { value: 'adventure', key: 'categories.adventure', icon: '🏔️' },
  { value: 'nature', key: 'categories.nature', icon: '🌿' },
  { value: 'wildlife', key: 'categories.wildlife', icon: '🦥' },
  { value: 'beach', key: 'categories.beach', icon: '🏖️' },
  { value: 'culture', key: 'categories.culture', icon: '🏛️' },
  { value: 'wellness', key: 'categories.wellness', icon: '🧘' }
] as const

// ============================================
// Default Images (Placeholders)
// ============================================
export const DEFAULT_IMAGES = {
  destinations: {
    guanacaste: 'https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=800&q=80',
    laFortuna: 'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=800&q=80',
    monteverde: 'https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?w=800&q=80',
    manuelAntonio: 'https://images.unsplash.com/photo-1586861203927-800a5acd4c90?w=800&q=80',
    caribe: 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80',
    valleCentral: 'https://images.unsplash.com/photo-1588708885923-98c04a8e4c3f?w=800&q=80'
  },

  // Generic fallbacks
  generic: {
    hotel: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80',
    tour: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80',
    beach: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
    mountain: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80'
  }
} as const

// ============================================
// Cache TTL Configuration (seconds)
// ============================================
export const CACHE_TTL = {
  // Lists
  vendorList: 300,        // 5 minutes
  blogList: 300,          // 5 minutes
  destinationList: 600,   // 10 minutes

  // Details
  vendorDetail: 600,      // 10 minutes
  blogDetail: 600,        // 10 minutes
  propertyDetail: 300,    // 5 minutes

  // Featured/High traffic
  featured: 180,          // 3 minutes
  landing: 120            // 2 minutes
} as const

// ============================================
// Pagination Defaults
// ============================================
export const PAGINATION = {
  defaultPage: 1,
  defaultPageSize: 20,
  maxPageSize: 100,
  searchPageSize: 12
} as const

// ============================================
// Contact Defaults (fallback values)
// ============================================
export const CONTACT = {
  defaultEmail: 'info@costaricatravel.dev',
  defaultPhone: '+506 8000-0000',
  defaultAddress: 'San José, Costa Rica'
} as const

// ============================================
// Search Filter Options (i18n-ready)
// ============================================
export const SEARCH_FILTERS = {
  difficulties: [
    { value: 'easy', key: 'filters.difficulty.easy', color: 'bg-green-100 text-green-700' },
    { value: 'medium', key: 'filters.difficulty.medium', color: 'bg-yellow-100 text-yellow-700' },
    { value: 'hard', key: 'filters.difficulty.hard', color: 'bg-red-100 text-red-700' }
  ],
  priceRanges: [
    { min: 0, max: 50, key: 'filters.price.under50' },
    { min: 50, max: 100, key: 'filters.price.50to100' },
    { min: 100, max: 200, key: 'filters.price.100to200' },
    { min: 200, max: null, key: 'filters.price.over200' }
  ],
  durations: [
    { min: 0, max: 4, key: 'filters.duration.halfDay' },
    { min: 4, max: 8, key: 'filters.duration.fullDay' },
    { min: 8, max: 24, key: 'filters.duration.multiDay' }
  ],
  sortOptions: [
    { value: 'popular', key: 'filters.sort.popular' },
    { value: 'price_asc', key: 'filters.sort.priceAsc' },
    { value: 'price_desc', key: 'filters.sort.priceDesc' },
    { value: 'rating', key: 'filters.sort.rating' },
    { value: 'newest', key: 'filters.sort.newest' }
  ],
  regions: [
    { value: 'guanacaste', key: 'regions.guanacaste' },
    { value: 'puntarenas', key: 'regions.puntarenas' },
    { value: 'limon', key: 'regions.limon' },
    { value: 'alajuela', key: 'regions.alajuela' },
    { value: 'sanjose', key: 'regions.sanjose' }
  ]
} as const

// ============================================
// API Configuration
// ============================================
export const API_CONFIG = {
  defaultTimeout: 30000,  // 30 seconds
  retryAttempts: 3,
  retryDelay: 1000        // 1 second
} as const
