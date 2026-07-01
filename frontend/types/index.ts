export interface ApiResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface Room {
  id: string
  property_id: string
  name: string
  description: string | null
  max_guests: number
  beds: number
  bed_type: string | null
  price_per_night: number
  weekend_price: number
  extra_guest_price: number
  cleaning_fee: number
  images: string[]
  is_available: boolean
}

export interface VendorInfo {
  id: string
  business_name: string
  business_type: string
  description: string | null
  logo_url: string | null
  rating: number | null
  total_reviews: number | null
}

export interface Property {
  id: string
  vendor_id: string
  name: string
  slug: string
  short_description: string | null
  description: string | null
  property_type: PropertyType
  category: string | null
  country: string
  province: string | null
  region: string
  city: string
  district: string | null
  address: string | null
  latitude: number | null
  longitude: number | null
  map_address: string | null
  cover_image: string | null
  images: string[]
  videos: string[]
  virtual_tour_url: string | null
  amenities: string[]
  features: string[]
  check_in_time: string
  check_out_time: string
  cancellation_policy: string | null
  house_rules: string | null
  important_info: string | null
  min_guests: number
  max_guests: number
  beds: number
  baths: number
  square_meters: number | null
  base_price: number
  currency: string
  weekend_price: number
  weekly_discount: number
  rating: number | null
  total_reviews: number
  is_featured: boolean
  is_active: boolean
  is_verified: boolean
  rooms: Room[]
  vendor: VendorInfo | null
  created_at: string
  updated_at: string
}

export type PropertyType = 'hotel' | 'resort' | 'villa' | 'apartment' | 'hostel' | 'eco_lodge' | 'cabin' | 'glamping' | 'boutique'

export interface CalendarDay {
  date: string
  available: boolean
  price_override?: number | null
  min_stay?: number | null
  max_stay?: number | null
  is_today: boolean
  is_past: boolean
}

export interface AvailabilityCalendarData {
  room_id: string
  dates: CalendarDay[]
}

export interface AvailabilityCheckResult {
  available: boolean
  alternative_dates: { check_in: string; check_out: string; nights: number }[]
}

export interface PricePreview {
  nights: number
  weekday_nights: number
  weekend_nights: number
  weekday_price: number
  weekend_price: number
  weekday_total: number
  weekend_total: number
  base_subtotal: number
  guests: number
  max_occupancy: number
  extra_guests: number
  extra_guest_price: number
  extra_guests_total: number
  weekly_discount_percent: number
  weekly_discount_amount: number
  subtotal: number
  commission_amount: number
  total: number
  currency: string
}

export interface Tour {
  id: string
  name: string
  slug: string
  short_description: string | null
  description: string | null
  category: TourCategory
  difficulty: TourDifficulty
  duration_hours: number
  max_group_size: number
  min_age: number | null
  cover_image: string | null
  images: string[]
  includes: string[]
  itinerary: ItineraryItem[]
  what_to_bring: string[]
  location: string
  region: string | null
  latitude: number | null
  longitude: number | null
  price: number
  rating: number | null
  review_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type TourCategory = 'adventure' | 'nature' | 'cultural' | 'water' | 'beach' | 'wildlife' | 'wellness' | 'gastronomy'
export type TourDifficulty = 'easy' | 'medium' | 'hard'

export interface ItineraryItem {
  time: string
  activity: string
  description?: string
}

export interface Destination {
  id: string
  name: string
  slug: string
  description: string | null
  country: string
  region: string | null
  province: string | null
  canton: string | null
  district: string | null
  latitude: number | null
  longitude: number | null
  zoom: number
  highlights: string[]
  things_to_do: string[]
  culture: string | null
  gastronomy: string | null
  history: string | null
  best_time: string | null
  weather_info: string | null
  getting_there: string | null
  local_tips: string | null
  safety_info: string | null
  language: string | null
  currency: string | null
  timezone: string | null
  phone_code: string | null
  visa_info: string | null
  emergency_numbers: string[]
  image: string | null
  gallery: string[]
  videos: string[]
  featured_photo: string | null
  seo_title: string | null
  seo_description: string | null
  seo_keywords: string[]
  is_featured: boolean
  is_active: boolean
  order: number
  created_at: string
  updated_at: string
}

export type DestinationRegion = 'Pacífico Norte' | 'Pacífico Central' | 'Pacífico Sur' | 'Norte' | 'Valle Central' | 'Caribe'

export interface Booking {
  id: string
  property_id: string | null
  tour_id: string | null
  user_id: string
  vendor_id: string
  room_id: string | null
  check_in: string
  check_out: string
  guests: number
  total_amount: number
  commission_amount: number
  status: BookingStatus
  confirmation_code: string
  stripe_payment_intent_id: string | null
  stripe_payment_status: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export type BookingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'refunded'

export interface User {
  id: string
  email: string
  full_name: string
  phone: string | null
  role: UserRole
  is_verified: boolean
  created_at: string
}

export type UserRole = 'client' | 'vendor' | 'admin' | 'super_admin' | 'agent' | 'customer_service'

export interface Vendor {
  id: string
  user_id: string
  business_name: string
  business_type: string | null
  stripe_connected: boolean
  stripe_account_id: string | null
  created_at: string
}

export interface BlogPost {
  id: string
  title: string
  slug: string
  excerpt: string | null
  content: string
  featured_image: string | null
  author: string
  category: string
  tags: string[]
  status: BlogPostStatus
  published_at: string | null
  created_at: string
  updated_at: string
}

export type BlogPostStatus = 'draft' | 'published' | 'archived'

export interface StaticPage {
  id: string
  title: string
  slug: string
  content: string
  template: string | null
  meta_title: string | null
  meta_description: string | null
  is_active: boolean
  show_in_footer: boolean
  show_in_header: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface StaticPageCreate {
  title: string
  slug: string
  content?: string
  template?: string | null
  meta_title?: string | null
  meta_description?: string | null
  is_active?: boolean
  show_in_footer?: boolean
  show_in_header?: boolean
  sort_order?: number
}

export interface StaticPageUpdate {
  title?: string
  slug?: string
  content?: string
  template?: string | null
  meta_title?: string | null
  meta_description?: string | null
  is_active?: boolean
  show_in_footer?: boolean
  show_in_header?: boolean
  sort_order?: number
}

export interface SEOSettings {
  id: string
  site_title_template: string
  default_meta_title: string
  default_meta_description: string
  default_meta_keywords: string[]
  google_site_verification: string
  robots_txt: string
  sitemap_enabled: boolean
  structured_data_enabled: boolean
  updated_by: string | null
  created_at: string
  updated_at: string
}

export interface SEOSettingsUpdate {
  site_title_template?: string
  default_meta_title?: string
  default_meta_description?: string
  default_meta_keywords?: string[]
  google_site_verification?: string
  robots_txt?: string
  sitemap_enabled?: boolean
  structured_data_enabled?: boolean
}

export interface MediaFile {
  id: string
  filename: string
  original_name: string
  mime_type: string
  size_bytes: number
  size_formatted: string
  url: string
  thumbnail_url: string | null
  alt_text: string | null
  folder: string | null
  uploaded_by: string | null
  uploaded_at: string
  used_in: string[]
}

export interface Vehicle {
  id: string
  name: string
  type: VehicleType
  capacity: number
  price_per_day: number
  image: string | null
  features: string[]
  location: string
  is_available: boolean
}

export type VehicleType = 'sedan' | 'suv' | 'van' | 'jeep' | 'luxury' | 'bus'

export interface Boat {
  id: string
  name: string
  type: BoatType
  capacity: number
  price_per_day: number
  image: string | null
  features: string[]
  location: string
  is_available: boolean
}

export type BoatType = 'sailboat' | 'catamaran' | 'yacht' | 'fishing' | 'speedboat'

export interface SearchResult {
  properties: Property[]
  tours: Tour[]
  destinations: Destination[]
  blog: BlogPost[]
}

export interface BookingStats {
  total_bookings: number
  pending: number
  confirmed: number
  completed: number
  cancelled: number
  total_revenue: number
  total_commission: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface TourSearchResponse {
  items: Tour[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface NewsletterResponse {
  success: boolean
  message: string
}

export interface SearchFilters {
  query?: string
  destination?: string
  category?: string
  difficulty?: string
  minPrice?: number
  maxPrice?: number
  minDuration?: number
  maxDuration?: number
  rating?: number
  date?: string
  travelers?: number
  sortBy?: 'price_asc' | 'price_desc' | 'rating' | 'popular' | 'newest'
}

export interface PaginationControls {
  currentPage: number
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
  totalItems: number
  itemsPerPage: number
}

// Marketing types
export interface Campaign {
  id: string
  name: string
  subject: string
  campaign_type: string
  status: string
  recipient_type: string
  total_recipients: number
  sent_count: number
  open_rate: number
  click_rate: number
  created_at: string
  scheduled_at?: string
  sent_at?: string
}

export interface CampaignCreate {
  name: string
  subject: string
  campaign_type: string
  html_content: string
  recipient_type: string
  template_id?: string
  scheduled_at?: string
  from_name?: string
  from_email?: string
}

export interface Template {
  id: string
  name: string
  description?: string
  template_type: string
  is_system: boolean
  preview_image?: string
  created_at: string
}

export interface CampaignAnalytics {
  campaign_id: string
  campaign_name: string
  total_recipients: number
  sent: number
  delivered: number
  opened: number
  clicked: number
  bounced: number
  open_rate: number
  click_rate: number
  click_to_open_rate: number
}

export interface MarketingOverview {
  campaigns: {
    total: number
    sent: number
    draft: number
  }
  engagement: {
    total_recipients: number
    total_sent: number
    total_opens: number
    total_clicks: number
    avg_open_rate: number
    avg_click_rate: number
  }
  recent_campaigns: Campaign[]
}

export interface VendorAnalytics {
  total_campaigns: number
  total_recipients: number
  total_opens: number
  total_clicks: number
  engagement_rate: number
}

export interface InboxMessage {
  id: string
  subject: string
  content: string
  is_from_customer: boolean
  is_read: boolean
  created_at: string
  vendor_id?: string
}

// Agency Landing Page
export interface AgencyLandingService {
  id: string
  name: string
  slug?: string
  cover_image: string | null
  price: number
  rating: number | null
  total_reviews: number
  service_type: string
  // Per-type extras
  property_type?: string
  category?: string
  city?: string
  region?: string
  location?: string
  duration_hours?: number
  brand?: string
  model?: string
  capacity?: number
  seats?: number
}

export interface AgencyLandingReview {
  id: string
  rating: number
  title: string | null
  comment: string | null
  user_name: string | null
  created_at: string
}

export interface AgencyLandingStats {
  total_properties: number
  total_tours: number
  total_vehicles: number
  total_boats: number
  total_transportation: number
  total_reviews: number
  total_bookings: number
  member_since: string | null
}

export interface AgencyLandingRanking {
  position: number
  total_vendors: number
}

export interface AgencyLandingData {
  id: string
  can_review: boolean
  eligible_booking_ids: string[]
  business_name: string
  business_slug: string
  business_type: string
  description: string | null
  logo_url: string | null
  cover_image: string | null
  phone: string | null
  email: string | null
  address: string | null
  rating: number | null
  total_reviews: number
  is_verified: boolean
  properties: AgencyLandingService[]
  properties_has_more: boolean
  tours: AgencyLandingService[]
  tours_has_more: boolean
  vehicles: AgencyLandingService[]
  vehicles_has_more: boolean
  boats: AgencyLandingService[]
  boats_has_more: boolean
  transportation: AgencyLandingService[]
  transportation_has_more: boolean
  reviews: AgencyLandingReview[]
  reviews_total: number
  reviews_average_rating: number
  stats: AgencyLandingStats
  ranking: AgencyLandingRanking
}

export interface EmailPreferences {
  marketing_emails: boolean
  booking_notifications: boolean
  promotional_emails: boolean
  newsletter: boolean
  email_frequency: string
  unsubscribed_all: boolean
  vendor_preferences: Record<string, boolean>
  categories: Record<string, boolean>
}
