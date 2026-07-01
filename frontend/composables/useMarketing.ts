import { ref, computed } from 'vue'
import type { Campaign, CampaignCreate, Template, CampaignAnalytics, MarketingOverview, VendorAnalytics, InboxMessage, EmailPreferences } from '~/types'

export const useMarketing = () => {
  const api = useApi()
  const asyncAction = useAsyncAction<null>({ defaultValue: null })

  // State
  const campaigns = ref<Campaign[]>([])
  const templates = ref<Template[]>([])
  const analytics = ref<CampaignAnalytics | null>(null)
  const overview = ref<MarketingOverview | null>(null)
  const vendorStats = ref<VendorAnalytics | null>(null)
  const inboxMessages = ref<InboxMessage[]>([])
  const emailPrefs = ref<EmailPreferences | null>(null)

  // ============ Super Admin Methods ============

  /**
   * List all campaigns (Super Admin)
   */
  const listAllCampaigns = async (params?: {
    status?: string
    campaign_type?: string
    page?: number
    limit?: number
  }): Promise<Campaign[]> => {
    const result = await asyncAction.execute(async () => {
      const response = await api.get<Campaign[]>('/marketing/admin/campaigns', params)
      campaigns.value = response
      return response
    })
    return result ?? []
  }

  const createCampaign = async (data: CampaignCreate) => {
    return asyncAction.execute(() => api.post('/marketing/admin/campaigns', data))
  }

  const sendCampaign = async (campaignId: string) => {
    return asyncAction.execute(() => api.post(`/marketing/admin/campaigns/${campaignId}/send`, {}))
  }

  const getCampaignAnalytics = async (campaignId: string) => {
    return asyncAction.execute(async () => {
      const response = await api.get<CampaignAnalytics>(`/marketing/admin/campaigns/${campaignId}/analytics`)
      analytics.value = response
      return response
    })
  }

  const listTemplates = async (params?: {
    template_type?: string
    include_system?: boolean
  }): Promise<Template[]> => {
    return asyncAction.execute(async () => {
      const response = await api.get<Template[]>('/marketing/admin/templates', params)
      templates.value = response
      return response
    }) ?? []
  }

  const createTemplate = async (data: {
    name: string
    description?: string
    template_type: string
    html_content: string
  }) => {
    return asyncAction.execute(() => api.post('/marketing/admin/templates', data))
  }

  const getMarketingOverview = async (): Promise<MarketingOverview | null> => {
    return asyncAction.execute(async () => {
      const response = await api.get<MarketingOverview>('/marketing/admin/analytics/overview')
      overview.value = response
      return response
    })
  }

  // ============ Vendor Methods ============

  const listVendorCampaigns = async (params?: {
    page?: number
    limit?: number
  }): Promise<Campaign[]> => {
    return asyncAction.execute(async () => {
      const response = await api.get<Campaign[]>('/marketing/vendor/campaigns', params)
      campaigns.value = response
      return response
    }) ?? []
  }

  const createVendorCampaign = async (data: CampaignCreate) => {
    return asyncAction.execute(() => api.post('/marketing/vendor/campaigns', data))
  }

  const vendorSendCampaign = async (campaignId: string) => {
    return asyncAction.execute(() => api.post(`/marketing/vendor/campaigns/${campaignId}/send`, {}))
  }

  const getVendorAnalytics = async (): Promise<VendorAnalytics | null> => {
    return asyncAction.execute(async () => {
      const response = await api.get<VendorAnalytics>('/marketing/vendor/analytics')
      vendorStats.value = response
      return response
    })
  }

  // ============ Inbox Methods ============

  const getInbox = async (params?: {
    page?: number
    limit?: number
    unread_only?: boolean
  }) => {
    return asyncAction.execute(async () => {
      const response = await api.get<{ messages: InboxMessage[] }>('/marketing/inbox', params)
      inboxMessages.value = response.messages || []
      return response
    })
  }

  const sendInboxMessage = async (data: {
    vendor_id?: string
    subject: string
    content: string
    message_type?: string
    booking_id?: string
    property_id?: string
    tour_id?: string
  }) => {
    return asyncAction.execute(() => api.post('/marketing/inbox/send', data))
  }

  const getUnreadCount = async (): Promise<number> => {
    const result = await asyncAction.execute(async () => {
      const response = await api.get<{ unread_count: number }>('/marketing/inbox/unread-count')
      return response.unread_count
    }, { silent: true, defaultValue: 0 })
    return result ?? 0
  }

  // ============ Email Preferences ============

  const getEmailPreferences = async (): Promise<EmailPreferences | null> => {
    return asyncAction.execute(async () => {
      const response = await api.get<EmailPreferences>('/marketing/preferences')
      emailPrefs.value = response
      return response
    })
  }

  const updateEmailPreferences = async (prefs: Partial<EmailPreferences>) => {
    return asyncAction.execute(() => api.put('/marketing/preferences', prefs))
  }

  return {
    // State
    campaigns: computed(() => campaigns.value),
    templates: computed(() => templates.value),
    analytics: computed(() => analytics.value),
    overview: computed(() => overview.value),
    vendorStats: computed(() => vendorStats.value),
    inboxMessages: computed(() => inboxMessages.value),
    emailPrefs: computed(() => emailPrefs.value),
    loading: computed(() => asyncAction.pending.value),
    error: computed(() => asyncAction.error.value),

    // Super Admin
    listAllCampaigns,
    createCampaign,
    sendCampaign,
    getCampaignAnalytics,
    listTemplates,
    createTemplate,
    getMarketingOverview,

    // Vendor
    listVendorCampaigns,
    createVendorCampaign,
    vendorSendCampaign,
    getVendorAnalytics,

    // Inbox
    getInbox,
    sendInboxMessage,
    getUnreadCount,

    // Preferences
    getEmailPreferences,
    updateEmailPreferences
  }
}
