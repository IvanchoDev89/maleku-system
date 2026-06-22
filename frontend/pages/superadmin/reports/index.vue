<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  DollarSign,
  ClipboardList,
  Users,
  Store,
  PieChart,
  Download,
  FileText,
  Calendar,
  ChevronDown,
  Trash2,
} from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const reportTypes = [
  { id: 'revenue', name: 'Revenue Report', icon: DollarSign, description: 'Ingresos por período, vendor y destino', color: 'text-emerald-600', bg: 'bg-emerald-100' },
  { id: 'bookings', name: 'Bookings Report', icon: ClipboardList, description: 'Tasas de conversión y cancelación', color: 'text-blue-600', bg: 'bg-blue-100' },
  { id: 'users', name: 'User Growth', icon: Users, description: 'Nuevos usuarios, activos y churn', color: 'text-violet-600', bg: 'bg-violet-100' },
  { id: 'vendors', name: 'Vendor Performance', icon: Store, description: 'Performance y comisiones por vendor', color: 'text-amber-600', bg: 'bg-amber-100' },
  { id: 'tax', name: 'Tax & Commission', icon: PieChart, description: 'Impuestos y reporte de comisiones', color: 'text-rose-600', bg: 'bg-rose-100' },
]

const dateRange = ref('last30days')
const format = ref('csv')
const generating = ref(false)
const loadingReports = ref(true)

const dateRangeOptions = [
  { value: 'last7days', label: 'Últimos 7 días' },
  { value: 'last30days', label: 'Últimos 30 días' },
  { value: 'last90days', label: 'Últimos 90 días' },
  { value: 'thisMonth', label: 'Este mes' },
  { value: 'lastMonth', label: 'Mes anterior' },
]

const formatOptions = [
  { value: 'csv', label: 'CSV' },
  { value: 'json', label: 'JSON' },
]

interface ReportEntry {
  id: string
  reportType: string
  reportName: string
  format: string
  generatedAt: string
  data: any
}

const recentReports = ref<ReportEntry[]>([])

const loadRecentReports = () => {
  loadingReports.value = true
  try {
    const stored = localStorage.getItem('superadmin_reports')
    recentReports.value = stored ? JSON.parse(stored) : []
  } catch {
    recentReports.value = []
  } finally {
    loadingReports.value = false
  }
}

const saveRecentReports = () => {
  localStorage.setItem('superadmin_reports', JSON.stringify(recentReports.value.slice(0, 20)))
}

const getReportIcon = (type: string) => {
  const found = reportTypes.find(r => r.id === type)
  return found?.icon || FileText
}

const getReportColor = (type: string) => {
  const found = reportTypes.find(r => r.id === type)
  return found?.color || 'text-gray-600'
}

const getReportBg = (type: string) => {
  const found = reportTypes.find(r => r.id === type)
  return found?.bg || 'bg-gray-100'
}

const generateReport = async (reportId: string) => {
  generating.value = true
  try {
    const days = dateRange.value === 'last7days' ? 7 : dateRange.value === 'last30days' ? 30 : 90
    const stats = await api.get('/superadmin/dashboard/stats')

    let reportData: any = { generated_at: new Date().toISOString(), period_days: days }
    let reportName = ''

    switch (reportId) {
      case 'revenue':
        reportData = { ...reportData, total_revenue: stats.total_revenue, net_revenue: stats.net_revenue, revenue_today: stats.revenue_today, revenue_this_month: stats.revenue_this_month, total_bookings: stats.total_bookings }
        reportName = `Revenue Report - ${new Date().toLocaleDateString()}`
        break
      case 'bookings':
        reportData = { ...reportData, total_bookings: stats.total_bookings, bookings_today: stats.bookings_today, bookings_this_week: stats.bookings_this_week, bookings_this_month: stats.bookings_this_month }
        reportName = `Bookings Report - ${new Date().toLocaleDateString()}`
        break
      case 'users':
        reportData = { ...reportData, total_users: stats.total_users, new_users_today: stats.new_users_today, active_users_today: stats.active_users_today, users_by_role: stats.users_by_role }
        reportName = `User Growth - ${new Date().toLocaleDateString()}`
        break
      case 'vendors':
        reportData = { ...reportData, total_vendors: stats.total_vendors, pending_vendors: stats.pending_vendors, active_vendors: stats.active_vendors, suspended_vendors: stats.suspended_vendors }
        reportName = `Vendor Performance - ${new Date().toLocaleDateString()}`
        break
      case 'tax':
        reportData = { ...reportData, net_revenue: stats.net_revenue, total_revenue: stats.total_revenue, commissions: (stats.total_revenue || 0) - (stats.net_revenue || 0) }
        reportName = `Tax & Commission - ${new Date().toLocaleDateString()}`
        break
    }

    const entry: ReportEntry = {
      id: `${reportId}_${Date.now()}`,
      reportType: reportId,
      reportName,
      format: format.value,
      generatedAt: new Date().toISOString(),
      data: reportData,
    }

    recentReports.value.unshift(entry)
    saveRecentReports()

    downloadReport(entry)
    toast.success(`Reporte "${reportName}" generado en ${format.value.toUpperCase()}`)
  } catch (e) {
    toast.error('Error al generar reporte')
  } finally {
    generating.value = false
  }
}

const downloadReport = (entry: ReportEntry) => {
  const content = format.value === 'json'
    ? JSON.stringify(entry.data, null, 2)
    : Object.entries(entry.data).map(([k, v]) => `${k},${v}`).join('\n')

  const mimeType = format.value === 'json' ? 'application/json' : 'text/csv'
  const ext = format.value === 'json' ? 'json' : 'csv'
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${entry.reportName.replace(/\s+/g, '_')}.${ext}`
  a.click()
  URL.revokeObjectURL(url)
}

const deleteReport = (id: string) => {
  recentReports.value = recentReports.value.filter(r => r.id !== id)
  saveRecentReports()
}

onMounted(() => {
  loadRecentReports()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Reportes</h1>
        <p class="mt-1 text-gray-500">Generación y exportación de reportes</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div class="flex flex-wrap gap-3 items-end">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Período</label>
          <UiSelect v-model="dateRange" :options="dateRangeOptions" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Formato</label>
          <UiSelect v-model="format" :options="formatOptions" />
        </div>
      </div>
    </div>

    <!-- Report Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="report in reportTypes"
        :key="report.id"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all group"
      >
        <div class="flex items-start justify-between">
          <div :class="[report.bg, report.color, 'w-12 h-12 rounded-xl flex items-center justify-center']">
            <component :is="report.icon" class="w-6 h-6" />
          </div>
          <button
            @click="generateReport(report.id)"
            :disabled="generating"
            class="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all disabled:opacity-50"
          >
            <UiSpinner v-if="generating" size="sm" color="primary" />
            {{ generating ? 'Generando...' : 'Generar' }}
            <ChevronDown v-if="!generating" class="w-4 h-4 -rotate-90" />
          </button>
        </div>
        <h3 class="mt-4 text-base font-semibold text-gray-900">{{ report.name }}</h3>
        <p class="mt-1 text-sm text-gray-500">{{ report.description }}</p>
      </div>
    </div>

    <!-- Recent Reports -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200">
      <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-base font-semibold text-gray-900">Reportes Generados</h3>
        <span class="text-sm text-gray-500">{{ recentReports.length }} reportes</span>
      </div>

      <div v-if="loadingReports" class="px-5 py-8 text-center text-gray-500">
        Cargando...
      </div>

      <div v-else-if="recentReports.length === 0" class="px-5 py-8 text-center">
        <FileText class="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p class="text-gray-500 text-sm">No hay reportes generados aún</p>
        <p class="text-gray-400 text-xs mt-1">Selecciona un tipo de reporte y haz clic en "Generar"</p>
      </div>

      <div v-else class="divide-y divide-gray-100">
        <div
          v-for="report in recentReports"
          :key="report.id"
          class="px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors group"
        >
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="getReportBg(report.reportType)">
              <component :is="getReportIcon(report.reportType)" class="w-5 h-5" :class="getReportColor(report.reportType)" />
            </div>
            <div>
              <div class="font-medium text-gray-900">{{ report.reportName }}</div>
              <div class="text-sm text-gray-500">
                {{ new Date(report.generatedAt).toLocaleString() }} • {{ report.format.toUpperCase() }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="downloadReport(report)"
              class="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1.5 px-3 py-1.5 hover:bg-amber-50 rounded-lg transition-colors"
            >
              <Download class="w-4 h-4" />
              Descargar
            </button>
            <button
              @click="deleteReport(report.id)"
              class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Eliminar reporte"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
