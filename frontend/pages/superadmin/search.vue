<template>
  <div class="space-y-6">
    <UiCard padding="md">
      <div class="flex items-center gap-4 mb-6">
        <div class="relative flex-1">
          <input
            v-model="query"
            type="text"
            placeholder="Buscar usuarios, proveedores, propiedades..."
            class="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all placeholder:text-gray-400"
            @keyup.enter="search"
          />
          <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        </div>
        <button
          @click="search"
          class="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
        >
          Buscar
        </button>
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400">
        <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
        Buscando...
      </div>

      <div v-else-if="error" class="p-4 bg-red-50 border border-red-200 rounded-xl">
        <p class="text-red-600 text-sm">{{ error }}</p>
      </div>

      <div v-else-if="results.length === 0 && searched" class="text-center py-12 text-gray-400">
        <Search class="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p class="font-medium text-gray-500">Sin resultados para "{{ query }}"</p>
        <p class="text-sm mt-1">Intenta con otros términos de búsqueda</p>
      </div>

      <div v-else-if="results.length > 0" class="space-y-4">
        <p class="text-sm text-gray-500">{{ results.length }} resultado(s) para "{{ query }}"</p>
        <div v-for="item in results" :key="item.id" class="flex items-start gap-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
          <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="item.iconBg">
            <component :is="item.icon" class="w-5 h-5" :class="item.iconColor" />
          </div>
          <div class="flex-1 min-w-0">
            <NuxtLink v-if="!item.is_property" :to="item.link" class="font-medium text-gray-900 hover:text-primary-600 transition-colors">
              {{ item.title }}
            </NuxtLink>
            <span v-else class="font-medium text-gray-500">{{ item.title }} <span class="text-xs text-gray-400 ml-1">(próximamente detalle)</span></span>
            <p class="text-xs text-gray-500 mt-0.5">{{ item.subtitle }}</p>
          </div>
          <NuxtLink :to="item.link" class="text-primary-600 hover:text-primary-700">
            <ChevronRight class="w-5 h-5" />
          </NuxtLink>
        </div>
      </div>

      <div v-else class="text-center py-12 text-gray-400">
        <Search class="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>Ingresa un término para buscar</p>
      </div>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
import { Search, ChevronRight, Users, Store, Building2, FileText } from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const route = useRoute()
const api = useApi()

const query = ref((route.query.q as string) || '')
const results = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const searched = ref(false)

const search = async () => {
  const q = query.value.trim()
  if (!q) return

  loading.value = true
  error.value = ''
  searched.value = true

  try {
    const [users, vendors, properties] = await Promise.allSettled([
      api.get<any[]>('/superadmin/users', { search: q, limit: 10 }).catch(() => []),
      api.get<any[]>('/superadmin/vendors', { search: q, limit: 10 }).catch(() => []),
      api.get<any[]>('/admin/properties', { search: q, limit: 10 }).catch(() => []),
    ])

    const items: any[] = []

    if (users.status === 'fulfilled') {
      for (const u of (users.value || [])) {
        items.push({
          id: `user-${u.id}`,
          title: u.full_name || u.email,
          subtitle: `${u.email} · ${u.role}`,
          link: `/superadmin/users/${u.id}`,
          icon: Users,
          iconBg: 'bg-primary-100',
          iconColor: 'text-primary-600',
        })
      }
    }

    if (vendors.status === 'fulfilled') {
      for (const v of (vendors.value || [])) {
        items.push({
          id: `vendor-${v.id}`,
          title: v.business_name,
          subtitle: `${v.owner_email || ''} · ${v.status}`,
          link: `/superadmin/vendors/${v.id}`,
          icon: Store,
          iconBg: 'bg-teal-100',
          iconColor: 'text-teal-600',
        })
      }
    }

    if (properties.status === 'fulfilled') {
      for (const p of (properties.value || [])) {
        items.push({
          id: `property-${p.id}`,
          title: p.name,
          subtitle: `${p.property_type || 'Propiedad'} · ${p.location || ''}`,
          link: `/superadmin/properties`,
          icon: Building2,
          iconBg: 'bg-blue-100',
          iconColor: 'text-blue-600',
          is_property: true,
        })
      }
    }

    results.value = items
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al realizar la búsqueda'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (route.query.q) search()
})
</script>
