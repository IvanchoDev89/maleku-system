<script setup lang="ts">
import { ref } from 'vue'
import { 
  DollarSign, 
  ClipboardList, 
  Users, 
  Store, 
  PieChart,
  Download,
  FileText,
  Calendar,
  ChevronDown
} from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const reportTypes = [
  { id: 'revenue', name: 'Revenue Report', icon: DollarSign, description: 'Ingresos por período, vendor y destino', color: 'text-emerald-600', bg: 'bg-emerald-100' },
  { id: 'bookings', name: 'Bookings Report', icon: ClipboardList, description: 'Tasas de conversión y cancelación', color: 'text-blue-600', bg: 'bg-blue-100' },
  { id: 'users', name: 'User Growth', icon: Users, description: 'Nuevos usuarios, activos y churn', color: 'text-violet-600', bg: 'bg-violet-100' },
  { id: 'vendors', name: 'Vendor Performance', icon: Store, description: 'Performance y comisiones por vendor', color: 'text-amber-600', bg: 'bg-amber-100' },
  { id: 'tax', name: 'Tax & Commission', icon: PieChart, description: 'Impuestos y reporte de comisiones', color: 'text-rose-600', bg: 'bg-rose-100' },
]

const dateRange = ref('last30days')
const format = ref('pdf')

const dateRangeOptions = [
  { value: 'last7days', label: 'Últimos 7 días' },
  { value: 'last30days', label: 'Últimos 30 días' },
  { value: 'last90days', label: 'Últimos 90 días' },
  { value: 'thisMonth', label: 'Este mes' },
  { value: 'lastMonth', label: 'Mes anterior' },
  { value: 'custom', label: 'Personalizado' },
]

const formatOptions = [
  { value: 'pdf', label: 'PDF' },
  { value: 'excel', label: 'Excel' },
  { value: 'csv', label: 'CSV' },
]

const toast = useToast()

const generateReport = (reportId: string) => {
  toast.success(`Generando reporte ${reportId} en formato ${format.value}`)
}
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
      <div class="flex flex-wrap gap-3">
        <div class="relative">
          <Calendar class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <UiSelect v-model="dateRange" :options="dateRangeOptions" placeholder="Últimos 7 días" />
        </div>
        <div class="relative">
          <FileText class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <UiSelect v-model="format" :options="formatOptions" placeholder="PDF" />
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
            class="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all"
          >
            Generar
            <ChevronDown class="w-4 h-4 -rotate-90" />
          </button>
        </div>
        <h3 class="mt-4 text-base font-semibold text-gray-900">{{ report.name }}</h3>
        <p class="mt-1 text-sm text-gray-500">{{ report.description }}</p>
      </div>
    </div>

    <!-- Recent Reports -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200">
      <div class="px-5 py-4 border-b border-gray-200">
        <h3 class="text-base font-semibold text-gray-900">Reportes Recientes</h3>
      </div>
      <div class="divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
              <DollarSign class="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <div class="font-medium text-gray-900">Revenue Report - Enero 2024</div>
              <div class="text-sm text-gray-500">Generado el 2024-02-01 • PDF</div>
            </div>
          </div>
          <button class="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1.5 px-3 py-1.5 hover:bg-amber-50 rounded-lg transition-colors">
            <Download class="w-4 h-4" />
            Descargar
          </button>
        </div>
        <div class="px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-violet-100 flex items-center justify-center">
              <Users class="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <div class="font-medium text-gray-900">User Growth - Q4 2023</div>
              <div class="text-sm text-gray-500">Generado el 2024-01-15 • Excel</div>
            </div>
          </div>
          <button class="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1.5 px-3 py-1.5 hover:bg-amber-50 rounded-lg transition-colors">
            <Download class="w-4 h-4" />
            Descargar
          </button>
        </div>
        <div class="px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
              <Store class="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <div class="font-medium text-gray-900">Vendor Performance - Diciembre 2023</div>
              <div class="text-sm text-gray-500">Generado el 2024-01-05 • PDF</div>
            </div>
          </div>
          <button class="text-amber-600 hover:text-amber-700 text-sm font-medium flex items-center gap-1.5 px-3 py-1.5 hover:bg-amber-50 rounded-lg transition-colors">
            <Download class="w-4 h-4" />
            Descargar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
